from machine import Pin
from utime import sleep

class led:
    def __init__(self):
        self.led=Pin(2,Pin.OUT) # onboard led
        self.led.value(0)

    def turnOn(self):
        self.led.value(1)

    def turnOff(self):
        self.led.value(0)
        
    def flash(self,speed):
        for i in range(3):
            sleep(speed)
            self.turnOn()
            sleep(speed)
            self.turnOff()
