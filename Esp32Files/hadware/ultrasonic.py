from machine import Pin
import utime

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
    
    def calibrateDistance(self,distError:int):
         
        farMeasure = 0

        # se hacen 4 medidas
        measurements = []
        for i in range(0,4):
            m = self.getMeasureUltrasonic()
            measurements.append(m)
        
        # se toma la mayor medida
        farMeasure = max(measurements)

        # si se supera el error maximo se limita
        if(distError <= farMeasure):
            distError = farMeasure // 10  # 10% del maximo

        self.distance_threshold = (farMeasure - distError)

        if self.distance_threshold < 0:
            self.distance_threshold = 5  # minimum threshold of 5 cm
            
        # self.max_distance = (farMeasure + distError)
        utime.sleep_us(1000)
    
    def __init__(self):

        print("esp32 ultrasonic init")

        self.PIN_TRIGGER=Pin(12,Pin.OUT,Pin.PULL_DOWN)
        self.PIN_TRIGGER.value(0)
        self.PIN_ECHO=Pin(14,Pin.IN,Pin.PULL_DOWN)

        # velocidad del sonido en atmosfera terrestre 343.2 m/s
        # /10k convertir cm/microsegundo 
        # /2 ida y vuelta del pulso 
        self.VelocidadSonido = 0.01716

        utime.sleep_ms(500)

        m1 = self.getMeasureUltrasonic()
        m2 = self.getMeasureUltrasonic()

        print("medidas dummy " + str(m1) + " " + str(m2))