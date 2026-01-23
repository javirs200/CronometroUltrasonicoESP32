from uasyncio import sleep_ms
from machine import Pin, SoftSPI
from lib.mfrc522 import MFRC522

class rfid:
    def __init__(self):
        self.sck = Pin(18, Pin.OUT)
        self.mosi = Pin(23, Pin.OUT)
        self.miso = Pin(19, Pin.OUT)
        self.sda = Pin(5, Pin.OUT)

        self.spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=self.sck, mosi=self.mosi, miso=self.miso)
        
        self.rdr = MFRC522(self.spi, self.sda)
        

    def read(self):
        try:
            (stat, tag_type) = self.rdr.request(self.rdr.REQIDL)
            if stat == self.rdr.OK:
                (stat, raw_uid) = self.rdr.anticoll()
                if stat == self.rdr.OK:
                    dec_string = ""
                    print("raw uid",raw_uid)
                    for b in raw_uid:
                        print("b ",b)
                        dec_string = dec_string + str(b)
                    print("dec_string ",dec_string)
                    return dec_string
            return None
        except Exception as e:
            print("ops somehing goes wrong on rfid" , e)
            return None