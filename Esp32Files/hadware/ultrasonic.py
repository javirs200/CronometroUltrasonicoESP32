from machine import Pin
import utime
from uasyncio import sleep

import machine
from machine import RTC

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
    
    def __init__(self,distError:int):

        self.rtc = machine.RTC()

        self.PIN_TRIGGER=Pin(12,Pin.OUT,0)
        self.PIN_ECHO=Pin(14,Pin.IN,0)

        # velocidad del sonido en atmosfera terrestre 343.2 m/s
        # /10k convertir cm/microsegundo 
        # /2 ida y vuelta del pulso 
        self.VelocidadSonido = 0.01716

        print("esp32 ultrasonic init")
        farMeasure = 0
        
        if (distError == None):
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