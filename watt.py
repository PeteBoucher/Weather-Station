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
    l = sensor.get_module()    
    target1 = l.get_serialNumber()

    sensor2 = YVoltage.FirstVoltage()
    m = sensor2.get_module()
    target2 = m.get_serialNumber()

    if sensor is None :
        die('No power module connected')
	
    if sensor2 is None :
	print('No voltage module connected')

    sensorPower= YPower.FindPower(target1 + '.power')
    sensorVoltage = YVoltage.FindVoltage(target2 + '.voltage1')

#DB connection
db = connect.getConnect()
r = db.cursor()

while True:
    if not(sensor.isOnline()):die('power device not online/connected')
    if not(sensor2.isOnline()):print('voltage device not online/connected')
    power = 0.0
    voltage = 0.0
    rangeCount = 300.0
    for x in xrange(1,301):
	power += sensorPower.get_currentValue()
	voltage += sensorVoltage.get_currentValue()
	time.sleep(0.2)

    resultPower = power / rangeCount
    resultVoltage = voltage / rangeCount
    r.execute('''INSERT INTO power (watt_charge,watt_usage,voltage) VALUES (%s,%s,%s)''',("%2.1f" % resultPower,3.5, resultVoltage))
    db.commit()

    print("Power :  "+ "%2.1f" % resultPower + "W (Ctrl-C to stop)")
    print("Voltage: "+ "%2.1f" % resultVoltage + "V")
    
    time.sleep(5)
