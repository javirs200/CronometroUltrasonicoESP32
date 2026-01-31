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
mode = "rally"  # Default mode
laps = 3       # Default number of laps
tries = 3      # Default number of tries

wait_time = 2000  # in ms

# --------state variables----------
started = False
finished = False
current_try = 0
current_lap = 0

temporal_time = 0
current_time = 0
previous_time = 0

#--------auxiliar functions---------
def on_ble_receive(data):
    """Callback when BLE receives data"""
    print("[CALLBACK] BLE data received!")
    try:
        message = data.decode('utf-8').strip()
        print(f"[CALLBACK] BLE received: {message}")
        # Flash LED when receiving data
        if leds:
            uasyncio.create_task(leds.flash(leds.BLUE, 100))
        if message.startswith("#"):
            global distError, mode, laps, tries
            try:
                command, value = message.split("=")
                command = command.strip().lower()
                value = value.strip()
                
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
                elif command == "#config":
                    response = (f"Current Config - Distance Error: {distError}cm, "
                                f"Mode: {mode}, Laps: {laps}, Tries: {tries}\n")
                else:
                    # usage instructions
                    response = ("Invalid command. Use:\n"
                                "#dist distance error in cm\n"
                                "#mode rally/circuit\n"
                                "#laps laps number\n"
                                "#tries tries number\n"
                                "#config gives current config\n")

                if ble:
                    ble.send(response)
                    uasyncio.create_task(leds.pluseFlash(leds.GREEN, 100))
                    print(f"[CALLBACK] Acknowledgement sent: {response.strip()}")

            except (ValueError, IndexError):
                error_msg = "Invalid command format. Use: #command=value\n"
                if ble:
                    ble.send(error_msg)
                uasyncio.create_task(leds.flash(leds.RED, 100))
                print(f"[CALLBACK] Error: {error_msg.strip()}")
    except Exception as e:
        print(f"[CALLBACK] Error processing BLE data: {e}")

async def do_send(messages):
    """Coroutine to send messages over BLE"""

    global ble

    print("Starting BLE send coroutine...")

    while True:
        # Send messages if connected and there are messages to send
        if ble and ble.is_connected and messages:
            data = messages.pop(0)
            ble.send(data)
        await uasyncio.sleep(0.2)

async def measureForever(ult:ultrasonic,messages:list[str]):
    """Coroutine to measure distance forever and handle timing logic"""
        
    global started, finished
    global temporal_time, current_time, previous_time
    global current_try, current_lap
    global mode, tries, laps

    # if holded infront of sensor wait until removed
    on_sensor = False

    print("Starting ultrasonic measurements...")

    try:
        while True:

            distance = ult.getMeasureUltrasonic()
            print("Distance: " + str(distance) + " cm |" + "Threshold: " + str(ult.distance_threshold) + " cm")

            if distance < ult.distance_threshold:

                print("Object detected within threshold.")

                temporal_time = utime.ticks_ms()

                current_time = utime.ticks_diff(temporal_time, previous_time)

                previous_time = temporal_time

                print("[DEBUG] Current Time: " + str(current_time) + " ms |" + str(wait_time) + " ms")

                if not on_sensor:

                    if current_time < wait_time:
                        on_sensor = True
                    else:
                        on_sensor = False
                        
                    # Leaved sensor or pass infront , send feedback to BT 
                    if not started and not finished:
                        started = True
                        message = "STARTED\n"
                        if leds:
                            await leds.pluseFlash(leds.GREEN, 50)

                    elif started and not finished:

                        message = "RUNNING\n"
                        messages.append(message)

                        # prompt actual situation
                        print(f"started and not finished - mode: {mode}, tries: {tries}, laps: {laps}, current_try: {current_try}, current_lap: {current_lap}")

                        if leds:
                            await leds.pluseFlash(leds.YELLOW, 50)

                        if mode == "rally":
                            if current_try < tries:
                                current_try += 1
                                message = f"TRY,{current_try},{current_time}\n"
                            else:
                                finished = True
                                message = f"FINISHED,Total Tries:{current_try}\n"
                                if leds:
                                    await leds.flash(leds.GREEN, 100)

                        elif mode == "circuit":
                            if current_lap < laps:
                                current_lap += 1
                                message = f"LAP,{current_lap},{current_time}\n"
                            else:
                                finished = True
                                message = f"FINISHED,Total Laps:{current_lap}\n"
                                if leds:
                                    await leds.flash(leds.GREEN, 100)

                        if leds:
                            await leds.pluseFlash(leds.GREEN, 50)
                            
                    messages.append(message)
                    print(f"Sent message: {message.strip()}")

                else:
                    
                    print("Object still in front of sensor, waiting for removal.")

            await uasyncio.sleep_ms(500)
                                
    except Exception as e:
        print("Measurement stopped in ultrasonic")
        print(e)

#--------main flow----------#
async def main():
    global ble, distError, leds

    #----------- setups ----------
    print('phase 0 , initialize neopixels (8 leds)')   
    leds = led()
    await leds.flash(leds.WHITE,200)
    leds.turnOff()

    await uasyncio.sleep_ms(500)

    print('phase 1 , initialize ultrasonic sensor')   
    await leds.pluseFlash(leds.YELLOW,200)
    ult = ultrasonic()
    leds.turnOff()

    await leds.flash(leds.YELLOW,100)

    await uasyncio.sleep_ms(500)
    
    # Initialize Bluetooth (aioble handles async internally)
    print("creating BLE service")
    ble = BLE(name="ESP32-Cronometro", rx_callback=on_ble_receive)
    await leds.flash(leds.BLUE,100)
    leds.turnOff()
    
    print('phase 2 , calibrate ultrasonic sensor , plese conect via bluetooth to configure')
    # # wait until connected
    while not ble.is_connected:
        await leds.circle(leds.BLUE, 200)
    
    await uasyncio.sleep_ms(500)

    # rapid flash to indicate connection
    await leds.flash(leds.GREEN, 100)
    # infinite one led circle to indicate ready
    await uasyncio.sleep_ms(500)

    print('plese send error setting ')
    while distError == 0:
        await leds.circle(leds.YELLOW, 200)

    ult.calibrateDistance(distError)

    await uasyncio.sleep_ms(500)
    
    await leds.flash(leds.YELLOW,200)
    leds.turnOff()

    print('ultrasonic initialized with distance threshold: ' + str(ult.distance_threshold) + ' cm')

    await uasyncio.sleep_ms(500)

    # #-------------- main runable -----------
    try:   
        print('phase 3 , infinite loop ultrasonic')

        # Create and run coroutines concurrently
        await uasyncio.gather(
            measureForever(ult, messages),
            do_send(messages)
        )

    except Exception as e:
        print('Exception:', e)
    finally:
        print('Cleaning up')
        if ble:
            ble.close()

if __name__ == '__main__':

    # set pin 12 to low , boot fails if high
    pin12 = Pin(12,Pin.OUT,Pin.PULL_DOWN)
    pin12.value(0)
    print('Booting...')

    try:
        uasyncio.run(main())
    except Exception as e:
        print('Error running main:', e)