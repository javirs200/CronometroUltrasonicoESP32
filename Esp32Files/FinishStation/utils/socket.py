import usocket as socket
#import socket
from uasyncio import sleep_ms
from utime import sleep

class mySocket:
    def __init__(self,host, port):
        for i in range(1,4):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                addr = socket.getaddrinfo(host,1)[0][-1][0]
                self.sock.connect((addr, port))
            except Exception as e:
                print('try ',i,' Exception mesage : ',e)
                self.sock.close()
                sleep(1)
        
    def close(self):
        self.sock.close()

    def sendtcp(self,m):
        try:
            enc = m.encode()
            sended = self.sock.write(m)
            print('sended : ',sended , 'bytes')
        except Exception as e:
            print('Exception mesage : ',e)
            close()