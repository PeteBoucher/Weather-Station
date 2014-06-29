#taken from: http://www.yoctopuce.com/EN/article/turn-your-raspberry-pi-into-a-network-multimeter and modified
import os
import sys
from yocto_api import *
from yocto_power import *
from yocto_voltage import *
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
    sensor2 = YVoltage.FindVoltage(target + '.voltage')

#DB connection
db = connect.getConnect()
r = db.cursor()

while True:
    if not(sensor.isOnline()):die('device not connected')
    
    power = 0.0
    voltage = 0.0
    
    for x in xrange(1,200):
	power += sensor.get_currentValue()
	voltage += sensor2.get_currentValue()
	time.sleep(200)

    resultPower = power / 200
    resultVoltage = voltage / 200
    r.execute('''INSERT INTO power (watt_charge,watt_usage,voltage) VALUES (%s,%s,%s)''',("%2.1f" % resultPower,3.5, resultVoltage))
    db.commit()

    time.sleep(5)

    print("Power :  "+ "%2.1f" % result + "W (Ctrl-C to stop)")
    
    
