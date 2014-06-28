#taken from: http://www.yoctopuce.com/EN/article/turn-your-raspberry-pi-into-a-network-multimeter and modified
import os
import sys
from yocto_api import *
from yocto_power import *
import time
import MySQLdb
import RPi.GPIO as GPIO
import connect

def die(msg):
    sys.exit(msg+' (die check USB cable)')

errmsg=YRefParam()

#target=sys.argv[1]
target = 'any'
# Setup the API to use local USB devices
if YAPI.RegisterHub("usb", errmsg)!= YAPI.SUCCESS:
    sys.exit("init error"+errmsg.value)

if target=='any':
    # retreive any Power sensor
    sensor = YPower.FirstPower()
    if sensor is None :
        die('No module connected')
else:
    sensor= YPower.FindPower(target + '.power')

#DB connection
db = connect.getConnect()
r = db.cursor()

while True:
    if not(sensor.isOnline()):die('device not connected')

    r.execute('''INSERT INTO power (watt_charge,watt_usage) VALUES (%s,%s)''',("%2.1f" % sensor.get_currentValue(),3.5))
    db.commit()

    time.sleep(55)

    print("Power :  "+ "%2.1f" % sensor.get_currentValue() + "W (Ctrl-C to stop)")
    YAPI.Sleep(1000)
    
