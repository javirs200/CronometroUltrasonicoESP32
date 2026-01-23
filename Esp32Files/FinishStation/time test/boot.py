import utime
from utils.mynetwork.networkManager import myNetwork
import ntptime

import machine
from machine import RTC

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def days_in_month(year, month):
    if month == 2:
        return 29 if is_leap_year(year) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31

def days_since_epoch(year, month, day):
    days = 0
    for y in range(1970, year):
        days += 366 if is_leap_year(y) else 365
    for m in range(1, month):
        days += days_in_month(year, m)
    days += day - 1
    return days

def datetime_to_nanoseconds(dt_tuple):
    print('arrives ' , dt_tuple)
    year, month, day, hour,weekday, minute, second, microsecond = dt_tuple
    days = days_since_epoch(year, month, day)
    total_seconds = days * 86400 + hour * 3600 + minute * 60 + second
    total_nanoseconds = total_seconds * 1_000_000_000 + microsecond * 1_000
    return total_nanoseconds
    
def main2():
    
    rtc = machine.RTC()
    
    net = myNetwork()
    print('phase 0 , wifi scan')
    net.connectOrReconect()
    print('phase 1 , sync time')
    ntptime.host = "0.es.pool.ntp.org"
    ntptime.settime()	# this queries the time from an NTP server
    
    dt_tuple = utime.localtime()
    year, month, day, hours, minutes, seconds, weekday, yearday = dt_tuple
    subseconds = 0
    rtc.datetime((year, month, day, weekday, hours, minutes, seconds, subseconds))
    
    nanoseconds = datetime_to_nanoseconds(rtc.datetime())
    
    print('rtc datetime ',rtc.datetime())
    print('dt_tuple ',dt_tuple)
    print('time_ns ',utime.time_ns())
    print('nanoseconds ',nanoseconds)
    
    nanoseconds1 = datetime_to_nanoseconds(rtc.datetime())
    utime.sleep(1)
    nanoseconds2 = datetime_to_nanoseconds(rtc.datetime())
    
    ns_dif =  nanoseconds1-nanoseconds2
    
    print('nsdif ',ns_dif)
        
if __name__ == '__main__':
    main2()
