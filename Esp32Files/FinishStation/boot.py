import utime
from hadware.ultrasonic import ultrasonic
import uasyncio

timestamps = []
messages = []

#--------auxiliar functions----------
async def do_send(messages):
        while True:
            # TODO Send time over bluetooth
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

    #----------- setups ----------
    print('phase 0 , initialize bluetooth')   
    # TODO setup bluetooth
    
    print('phase 1 , setup over bluetooth')   
    # TODO setup over bluetooth
    distError = 20

    print('phase 2 , initialize ultrasonic')   
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