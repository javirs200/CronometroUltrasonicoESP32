import utime
from hadware.ultrasonic import ultrasonic
from hadware.rfid import rfid
from utils.mynetwork.networkManager import myNetwork
from utils.socket import mySocket
import uasyncio

import ntptime
import machine
from machine import RTC

from utils.timeConverter import datetime_to_nanoseconds

uidsScaned = []
timestamps = []
messages = []

global farMeasure
global distError

#--------auxiliar functions----------#
async def do_read(rf,timestamps,messages):
    while True:
        # print("read rfid")
        uid = rf.read()
        if len(timestamps) > 0 and uid is not None:
            m = "timestamp:" + str(timestamps.pop(0)) + "|uid:" + str(uid)
            print("send ",m)
            #apped m to socket queuque
            messages.append(m)
        await uasyncio.sleep(0.2)
        
async def do_send(soc,messages):
        while True:
            # print("read rfid")
            if len(messages) > 0:
                soc.sendtcp(messages.pop(0))
            await uasyncio.sleep(0.2)

#--------main flow----------#
def main():
    rtc = machine.RTC()
    net = myNetwork()
    print('phase 0 , wifi scan')
    net.connectOrReconect()

    print('phase 1 , sync time')
    ntptime.host = "0.es.pool.ntp.org"
    ntptime.settime()	# this queries the time from an NTP server for init rtc
    dt_tuple = utime.localtime()
    year, month, day, hours, minutes, seconds, weekday, yearday = dt_tuple
    rtc.datetime((year, month, day, weekday, hours, minutes, seconds, 0))# set rtc time
    
    print('phase 2 , wifi conected , initialize Tcp Socket')
    soc = mySocket('raspberrypi.local',12345) # raspberrypi.mshome.net host name when ap is from windows 11 , raspberry.local host name when ap is from android
    print(soc)
    print('phase 3 , Socket conected, initialize ultrasonic and rfid')   
    ult = ultrasonic()
    rf = rfid()

    try:   
        print('wait to start 1000 ms')
        utime.sleep_ms(1000)
        print('phase 2 , ifinite loop ultrasonic and rfid')
        loop = uasyncio.get_event_loop()
        try:
            utime.sleep_ms(1000)
            net.connectOrReconect()
            # run coroutines concurrently
            loop.create_task(ult.measureForever(timestamps))
            loop.create_task(do_read(rf,timestamps,messages))
            loop.create_task(do_send(soc,messages))
            loop.run_forever()
        except Exception as e:
            print('Exception ',e)
            loop.stop()
            loop.close()
            print('reconection')
            pass        
    except:
        print('end')
        pass   

if __name__ == '__main__':
    main()