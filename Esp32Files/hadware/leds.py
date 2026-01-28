from machine import Pin
from neopixel import NeoPixel
from uasyncio import sleep_ms

# neopixel led control

class led:

    #color definitions
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    def __init__(self):
        self.pin=Pin(13,Pin.OUT) 
        self.np = NeoPixel(self.pin, 8)   
        for i in range(0,8):
            self.np[i] = (0, 0, 0) 
        self.np.write()
        
    def turnOn(self, color:tuple[int,int,int], intensity=50):
        self.color = (int(color[0]*intensity/100),int(color[1]*intensity/100),int(color[2]*intensity/100))
        for i in range(0,8):
            self.np[i] = self.color
        self.np.write()

    def turnOnPluse(self, color:tuple[int,int,int], intensity=50):
        self.color = (int(color[0]*intensity/100),int(color[1]*intensity/100),int(color[2]*intensity/100))
        for i in [1,3,5,7]:
            self.np[i] = self.color
        self.np.write()

    def turnOff(self):
        for i in range(0,8):
            self.np[i] = (0, 0, 0)
        self.np.write()
        
    async def flash(self,color:tuple[int,int,int],speed):
        for i in range(3):
            await sleep_ms(speed)
            self.turnOn(color,intensity=50)
            await sleep_ms(speed)
            self.turnOff()

    async def pluseFlash(self,color:tuple[int,int,int],speed):
        for i in range(3):
            await sleep_ms(speed)
            self.turnOnPluse(color,intensity=50)
            await sleep_ms(speed)
            self.turnOff()

    async def circle(self,color:tuple[int,int,int],speed):
        for i in range(0,8):
            self.turnOff()
            self.np[i] = color
            self.np.write()
            await sleep_ms(speed)

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
