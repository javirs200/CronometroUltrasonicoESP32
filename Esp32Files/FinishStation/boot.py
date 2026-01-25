import utime
from hadware.ultrasonic import ultrasonic
from hadware.leds import led
from hadware.bluetooth import BLE
import uasyncio

timestamps = []
messages = []
ble = None
distError = 5  # Default distance error in cm

#--------auxiliar functions----------
def on_ble_receive(data):
    """Callback when BLE receives data"""
    try:
        message = data.decode('utf-8').strip()
        print(f"BLE received: {message}")
        if message.startswith("#dist"):
            global distError
            distError = int(message.split("=")[1])
            print(f"Distance error set to: {distError}")
    except Exception as e:
        print(f"Error processing BLE data: {e}")

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
                await utime.sleep_ms(200)                              
        except Exception as e:
            print("Measurement stopped in ultrasonic")
            print(e)

#--------main flow----------#
def main():
    global ble, distError

    #----------- setups ----------
    print('phase 0 , initialize bluetooth and neopixels (8 leds)')   
    leds = led()
    leds.flash(1500)
    leds.turnOff()
    
    # Initialize Bluetooth
    ble = BLE(name="ESP32-Cronometro", rx_callback=on_ble_receive)
    utime.sleep_ms(500)
    leds.flash(300)

    print('phase 1 , setup over bluetooth')   
    # Wait 2000 ms to receive distance error parameter over BLE
    start_time = utime.ticks_ms()
    while utime.ticks_ms() - start_time < 2000:
        if ble.is_connected:
            leds.flash(200)
        utime.sleep_ms(100)
    
    print(f'phase 2 , initialize ultrasonic with distance error: {distError}cm')   
    ult = ultrasonic(distError)

    #-------------- main runable -----------
    try:   
        print('wait to start 1000 ms')
        utime.sleep_ms(1000)
        print('phase 3 , ifinite loop ultrasonic')
        loop = uasyncio.get_event_loop()
        try:
            utime.sleep_ms(1000)
            # run coroutines concurrently
            loop.create_task(measureForever(ult,timestamps))
            loop.create_task(do_send(messages))
            loop.run_forever()
        except Exception as e:
            print('Exception ',e)
            loop.stop()
            loop.close()
            pass        
    except:
        print('end')
        pass   

if __name__ == '__main__':
    main()