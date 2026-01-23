from machine import Pin
import utime
from uasyncio import sleep

import machine
from machine import RTC

from utils.timeConverter import datetime_to_nanoseconds

class ultrasonic:
    def getMeasureUltrasonic(self):
        distance=0
        self.PIN_TRIGGER.value(0)
        utime.sleep_us(100)
        self.PIN_TRIGGER.value(1)
        utime.sleep_us(10)
        self.PIN_TRIGGER.value(0)
        # esparar hasta recibir una lectura del pin echo
        while not self.PIN_ECHO.value():
            pass
        pingStart=utime.ticks_us()
        while self.PIN_ECHO.value():
            pass
        pingStop=utime.ticks_us()
        pingTime=utime.ticks_diff(pingStop,pingStart)

        # d=v*t 
        distance=self.VelocidadSonido*pingTime
        return int(distance)
    
    def __init__(self):

        self.rtc = machine.RTC()

        self.PIN_TRIGGER=Pin(4,Pin.OUT,0)
        self.PIN_ECHO=Pin(14,Pin.IN,0)

        # velocidad del sonido en atmosfera terrestre 343.2 m/s
        # /10k convertir cm/microsegundo 
        # /2 ida y vuelta del pulso 
        self.VelocidadSonido = 0.01716

        print("esp32 ultrasonic init")
        farMeasure = 0
        distError = 20
        for i in range(0,4):
            m = self.getMeasureUltrasonic()
            print("claibration " + str(m))
            if(m > farMeasure):
                farMeasure = m
        
            self.treshold = (farMeasure - distError)

            self.dist = (farMeasure + distError)

        print("treshold " + str(self.treshold))
        print("farMeasure " + str(farMeasure))  
        print("ready to measures")

    async def measureForever(self,timestamps):
        try:
            while True:
                self.dist = self.getMeasureUltrasonic()
                print("distance measured " + str(self.dist) + "cm")
                print("timestamps ",timestamps)
                if self.dist < self.treshold  :
                    print("distance less than treshold")
                    rtctimetuple = self.rtc.datetime()
                    #print("rtc time tuple ",rtctimetuple)
                    nanoseconds = datetime_to_nanoseconds(rtctimetuple)
                    timestamps.append(nanoseconds)
                await sleep(0.2)                              
        except Exception as e:
            print("Measurement stopped in ultrasonic")
            print(e)