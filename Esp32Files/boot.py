from machine import Pin
import utime
from hadware.ultrasonic import ultrasonic
from hadware.leds import led
from hadware.bluetooth import BLE
import uasyncio

#--------queues----------
messages = []

# Global instances
ble = None
leds = None

# --------configuration variables----------
distError = 0  # Default distance error in cm
mode = "circuit"  # Default mode ("rally" or "circuit")
laps = 3       # Default number of laps
tries = 3      # Default number of tries

wait_time = 2000  # in ms

# --------mode configuration----------
mode_config = {
    "rally": {
        "started_msg": "STARTED RALLY MODE",
        "counter_format": "TRY {}",
        "finish_format": "TRY {}",
        "counter_var_name": "current_try",
        "max_var_name": "tries",
    },
    "circuit": {
        "started_msg": "STARTED CIRCUIT MODE",
        "counter_format": "LAP: {}",
        "finish_format": "LAP: {}",
        "counter_var_name": "current_lap",
        "max_var_name": "laps",
    }
}

# --------state variables----------
started = False
finished = False
current_try = 0
current_lap = 0

temporal_time = 0
current_time = 0
previous_time = 0

direction = 0 # 0 when car passes in front of sensor for the first time, 1 when returns, used only in rally mode to count tries

#--------auxiliar functions---------

def reset_state():
    """Reset the state variables for a new measurement session"""
    global started, finished
    global current_try, current_lap
    global temporal_time, current_time, previous_time
    global direction
    started = False
    finished = False
    current_try = 0
    current_lap = 0

    temporal_time = 0
    current_time = 0
    previous_time = 0

    direction = 0

def format_time(ms:int) -> str:
    """Format time in milliseconds to a string MM:SS.sss"""
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    return f"{minutes:02}:{seconds:02}.{milliseconds:03}"

def on_ble_receive(data):
    """Callback when BLE receives data"""
    # print("[CALLBACK] BLE data received!")
    try:
        message = data.decode('utf-8').strip()
        # print(f"[CALLBACK] BLE received: {message}")
        # Flash LED when receiving data
        if leds:
            uasyncio.create_task(leds.flash(leds.BLUE, 100))
        if message.startswith("#"):
            global distError, mode, laps, tries
            try:
                command, value = message.split("=")
                command = command.strip().lower()
                value = value.strip()
                
                if command == "#config":
                    response = (f"Current Config - Distance Error: {distError}cm, "
                                f"Mode: {mode}, Laps: {laps}, Tries: {tries}\n")
                elif command == "#reset":
                    reset_state()
                    response = "State has been reset for a new session.\n"
                elif command in ["#dist", "#mode", "#laps", "#tries"]:
                    if not started:
                        if command == "#dist":
                            distError = int(value)
                            response = f"Distance error recived {distError}cm\n"
                        elif command == "#mode":
                            mode = value.lower()
                            if mode in ["rally", "circuit"]:
                                response = f"Mode updated to {mode}\n"
                            else:
                                response = "Invalid mode. Use 'rally' or 'circuit'\n"
                        elif command == "#laps":
                            laps = int(value)
                            response = f"Laps updated to {laps}\n"
                        elif command == "#tries":
                            tries = int(value)
                            response = f"Tries updated to {tries}\n"
                    else:
                        response = "Cannot change configuration while a session is active. Please reset first.\n"
                else: # usage instructions for invalid command
                    response = ("Invalid command. Use:\n"
                                "#dist distance error in cm\n"
                                "#mode rally/circuit\n"
                                "#laps laps number\n"
                                "#tries tries number\n"
                                "#config gives current config\n")
                if ble:
                    ble.send(response)
                    uasyncio.create_task(leds.pluseFlash(leds.GREEN, 100))
                    # print(f"[CALLBACK] Acknowledgement sent: {response.strip()}")

            except (ValueError, IndexError):
                error_msg = "Invalid command format. Use: #command=value\n"
                if ble:
                    ble.send(error_msg)
                uasyncio.create_task(leds.flash(leds.RED, 100))
                # print(f"[CALLBACK] Error: {error_msg.strip()}")
    except Exception as e:
        print(f"[CALLBACK] Error processing BLE data: {e}")

async def do_send(messages):
    """Coroutine to send messages over BLE"""

    global ble

    # print("Starting BLE send coroutine...")

    while True:
        # Send messages if connected and there are messages to send
        if ble and ble.is_connected and messages:
            data = messages.pop(0)
            ble.send(data)
        await uasyncio.sleep(0.2)

async def handle_session_start(mode_name):
    """Handle session start messaging and LED feedback for both modes"""
    global tries, laps, direction
    
    config = mode_config[mode_name]
    message = config["started_msg"] + "\n"
    message += f"Number of {config['max_var_name']}: {tries if config['max_var_name'] == 'tries' else laps}\n"
    
    if mode_name == "rally":
        direction = 0  # reset direction at start
    
    if leds:
        await leds.pluseFlash(leds.GREEN, 300)
    
    return message

async def handle_session_finish(counter_value, current_time_ms):
    """Handle session finish messaging and LED feedback for both modes"""
    global finished, mode
    
    config = mode_config[mode]
    messages_to_add = []
    
    if not finished:
        # Add the final counter message
        final_message = f"{config['finish_format'].format(counter_value + 1)}  Time:  {format_time(current_time_ms)}\n"
        messages_to_add.append(final_message)
    
    finished = True
    messages_to_add.append("FINISHED !!!\n")
    
    if leds:
        await leds.flash(leds.GREEN, 100)
    
    return messages_to_add

async def handle_counter_increment(counter_value, max_value, current_time_ms):
    """Handle counter increment and message formatting for both modes"""
    global mode
    
    config = mode_config[mode]
    
    if counter_value < max_value - 1:
        new_counter = counter_value + 1
        message = f"{config['counter_format'].format(new_counter)}  Time:  {format_time(current_time_ms)}\n"
        return new_counter, message
    else:
        return counter_value, None

async def measureForever(ult:ultrasonic,messages:list[str]):
    """Coroutine to measure distance forever and handle timing logic"""
        
    global started, finished
    global temporal_time, current_time, previous_time
    global current_try, current_lap
    global mode, tries, laps
    global direction

    # if holded infront of sensor wait until removed
    on_sensor = False

    # print("Starting ultrasonic measurements...")

    try:
        while True:

            distance = ult.getMeasureUltrasonic()
            # print("Distance: " + str(distance) + " cm |" + "Threshold: " + str(ult.distance_threshold) + " cm")

            if distance < ult.distance_threshold:

                # print("Object detected within threshold.")

                temporal_time = utime.ticks_ms()

                current_time = utime.ticks_diff(temporal_time, previous_time)

                previous_time = temporal_time

                # # print("[DEBUG] Current Time: " + str(current_time) + " ms |" + str(wait_time) + " ms")

                if current_time < wait_time:
                    on_sensor = True
                else:
                    on_sensor = False

                if not on_sensor:
                        
                    # Leaved sensor or pass infront , send feedback to BT 
                    if not started and not finished:
                        started = True
                        message = await handle_session_start(mode)

                    elif started and not finished:

                        message = "RUNNING\n"
                        messages.append(message)

                        # prompt actual situation
                        # # print(f"[DEBUG] started and not finished - mode: {mode}, tries: {tries}, laps: {laps}, current_try: {current_try}, current_lap: {current_lap}")

                        if leds:
                            await leds.pluseFlash(leds.YELLOW, 100)

                        if mode == "rally":
                            # print(f"[DEBUG] Rally mode - direction: {direction}, current_try: {current_try}, tries: {tries}")
                            if direction == 1: # returned 
                                direction = 0
                                current_try, counter_msg = await handle_counter_increment(current_try, tries, current_time)
                                
                                if counter_msg:
                                    message = counter_msg
                                else:
                                    # Reached max tries, handle finish
                                    finish_messages = await handle_session_finish(current_try, current_time)
                                    for msg in finish_messages:
                                        messages.append(msg)
                                    message = None  # Don't append again at the end
                            elif direction == 0: # passed infront
                                direction = 1
                                message = None  # Don't send message on first pass

                        elif mode == "circuit":
                            current_lap, counter_msg = await handle_counter_increment(current_lap, laps, current_time)
                            
                            if counter_msg:
                                message = counter_msg
                            else:
                                # Reached max laps, handle finish
                                finish_messages = await handle_session_finish(current_lap, current_time)
                                for msg in finish_messages:
                                    messages.append(msg)
                                message = None  # Don't append again at the end

                    # queue the message if it exists
                    if message is not None:
                        messages.append(message)
                    
                else:
                    # still on sensor , do not register multiple times
                    pass
                    
            await uasyncio.sleep_ms(50)
                                
    except Exception as e:
        print("Measurement stopped in ultrasonic")
        # print(e)

#--------main flow----------#
async def main():
    global ble, distError, leds

    #----------- setups ----------
    # print('phase 0 , initialize neopixels (8 leds)')   
    leds = led()
    await leds.flash(leds.WHITE,200)
    leds.turnOff()

    await uasyncio.sleep_ms(500)

    # print('phase 1 , initialize ultrasonic sensor')   
    await leds.pluseFlash(leds.YELLOW,200)
    ult = ultrasonic()
    leds.turnOff()

    await leds.flash(leds.YELLOW,100)

    await uasyncio.sleep_ms(500)
    
    # Initialize Bluetooth (aioble handles async internally)
    # print("creating BLE service")
    ble = BLE(name="ESP32-Cronometro", rx_callback=on_ble_receive)
    await leds.flash(leds.BLUE,500)
    leds.turnOff()
    
    # print('phase 2 , calibrate ultrasonic sensor , plese conect via bluetooth to configure')
    # # wait until connected
    while not ble.is_connected:
        await leds.circle(leds.BLUE, 200)
    
    await uasyncio.sleep_ms(500)

    # rapid flash to indicate connection
    await leds.flash(leds.GREEN, 100)
    # infinite one led circle to indicate ready
    await uasyncio.sleep_ms(500)

    # print('plese send error setting ')
    while distError == 0:
        await leds.circle(leds.YELLOW, 200)

    ult.calibrateDistance(distError)

    await uasyncio.sleep_ms(500)
    
    await leds.flash(leds.YELLOW,200)
    leds.turnOff()

    # print('ultrasonic initialized with distance threshold: ' + str(ult.distance_threshold) + ' cm')

    await uasyncio.sleep_ms(500)

    # #-------------- main runable -----------
    try:   
        # print('phase 3 , infinite loop ultrasonic')

        # Create and run coroutines concurrently
        await uasyncio.gather(
            measureForever(ult, messages),
            do_send(messages)
        )

    except Exception as e:
        print('Exception:', e)
    finally:
        # print('Cleaning up')
        if ble:
            ble.close()

if __name__ == '__main__':

    # set pin 12 to low , boot fails if high
    pin12 = Pin(12,Pin.OUT,Pin.PULL_DOWN)
    pin12.value(0)
    # print('Booting...')

    try:
        uasyncio.run(main())
    except Exception as e:
        print('Error running main:', e)