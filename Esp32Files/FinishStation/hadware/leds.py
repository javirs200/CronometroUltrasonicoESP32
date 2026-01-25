from machine import Pin
# from utime import sleep
from neopixel import NeoPixel

# neopixel led control

class led:
    def __init__(self):
        self.pin=Pin(0,Pin.OUT) 
        self.np = NeoPixel(self.pin, 8)   
        for i in range(0,8):
            self.np[i] = (0, 0, 0) 
        self.np.write()
        
    def turnOn(self):
        for i in range(0,8):
            self.np[i] = (255, 255, 255)
        self.np.write()

    def turnOff(self):
        for i in range(0,8):
            self.np[i] = (0, 0, 0)
        self.np.write()
        
    def flash(self,speed):
        for i in range(3):
            sleep(speed)
            self.turnOn()
            sleep(speed)
            self.turnOff()

    def changeOne(self,position:int,color:tuple[int,int,int]):
        self.np[position] = color
        self.np.write()
        pass

    def changeOneWithoutWrite(self,position:int,color:tuple[int,int,int]):
        self.np[position] = color
        pass

    def writeToPixels(self):
        self.np.write()
        pass
