import utime
from hadware.ultrasonic import ultrasonic
from hadware.leds import led
from hadware.bluetooth import BLE
import uasyncio

timestamps = []
messages = []
ble = None
leds = None
distError = 5  # Default distance error in cm

#--------auxiliar functions----------
def on_ble_receive(data):
    """Callback when BLE receives data"""
    print("[CALLBACK] BLE data received!")
    try:
        message = data.decode('utf-8').strip()
        print(f"[CALLBACK] BLE received: {message}")
        # Flash LED when receiving data
        if leds:
            uasyncio.create_task(leds.flash(leds.BLUE, 100))
        if message.startswith("#dist"):
            global distError
            distError = int(message.split("=")[1])
            print(f"[CALLBACK] Distance error set to: {distError}")
            # Acknowledge setting change
            if ble:
                print(f"[CALLBACK] Sending acknowledgement")
                ble.send(f"Distance error updated to {distError}cm\n")
                leds.flash(leds.GREEN, 100)
                print(f"[CALLBACK] Acknowledgement sent")
    except Exception as e:
        print(f"[CALLBACK] Error processing BLE data: {e}")

async def do_send(messages):
        while True:
            if ble and ble.is_connected and messages:
                data = messages.pop(0)
                ble.send(data)
            await uasyncio.sleep(0.2)

async def measureForever(ult:ultrasonic,timestamps):
        # TODO change logic
        try:
            while True:
                ult.dist = ult.getMeasureUltrasonic()
                print("distance measured " + str(ult.dist) + "cm")
                print("timestamps ",timestamps)
                if ult.dist < ult.treshold  :
                    print("distance less than treshold")
                    # TODO calculate time
                await uasyncio.sleep_ms(200)                              
        except Exception as e:
            print("Measurement stopped in ultrasonic")
            print(e)

#--------main flow----------#
async def main():
    global ble, distError, leds

    #----------- setups ----------
    print('phase 0 , initialize bluetooth and neopixels (8 leds)')   
    leds = led()
    await leds.flash(leds.WHITE,500)
    leds.turnOff()
    
    # Initialize Bluetooth (aioble handles async internally)
    print("creating BLE service")
    ble = BLE(name="ESP32-Cronometro", rx_callback=on_ble_receive)
    await uasyncio.sleep_ms(500)
    # Create tasks for connection wait and LED feedback

    # wait until connected
    while not ble.is_connected:
        await leds.circle(leds.BLUE, 200)
    
    # rapid flash to indicate connection
    await leds.flash(leds.GREEN, 100)
    # infinite one led circle to indicate ready
    
    print(f'phase 2 , initialize ultrasonic with distance error: {distError}cm')   
    # ult = ultrasonic(distError)

    # #-------------- main runable -----------
    try:   
        print('wait to start 1000 ms')
        await uasyncio.sleep_ms(1000)
        print('phase 3 , infinite loop ultrasonic')

        # Create and run coroutines concurrently
        await uasyncio.gather(
            # measureForever(ult, timestamps),
            do_send(messages)
        )
    except Exception as e:
        print('Exception:', e)
    finally:
        print('Cleaning up')
        if ble:
            ble.close()

if __name__ == '__main__':
    try:
        uasyncio.run(main())
    except Exception as e:
        print('Error running main:', e)