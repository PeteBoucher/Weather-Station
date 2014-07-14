import os
import glob
import time
import MySQLdb
import RPi.GPIO as GPIO
import datetime
import re
import connect

#By Lars-Martin Hejll
#http://softwarefun.org

#temp from BS18B20 sensor

#initialize device
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#now the "one-wire" device is visible at /sys/bus/w1/devices (base_folder)
#"one-wire" device pin is GPIO4 (physical pin number 7)

#setup GPIO's for: 

fan_pin = 15 #Fan unit 15 (ph) 
heater_pin = 11 #Heater 18 (ph) 
door_pin = 22 #Linear actuator/door 22 (ph)

GPIO.setmode(GPIO.BCM)

GPIO.setup(fan_pin, GPIO.OUT)
GPIO.setup(heater_pin, GPIO.OUT)
GPIO.setup(door_pin, GPIO.OUT)

#w1 is a virtual folder
device_base_folder = '/sys/bus/w1/devices/'
device_folder = glob.glob(device_base_folder + '28-00000384c1bb')[0]
device_file = device_folder + '/w1_slave'
    
#get raw temp from sensor        
def read_temp_raw():
        s = open(device_file, 'r')
        raw = s.readlines()
        s.close()
    	return raw
		#returns an array of sensor data (BS18B20)
		#with the temp from sensor in index(1).
		
def read_temp():
        
        #raw array format: ['73 00 4b 46 7f ff 0d 10 7c : crc=7c YES\n', '73 00 4b 46 7f ff 0d 10 7c t=14800\n']
        #actual value= 14800 => 14.800 C
        #searching for pattern 't=' in array
        temp_string_unscaled = re.search('t=(\d+)',str(read_temp_raw())).group(1);
	return float(temp_string_unscaled) / 1000;
		

#init setup, set values high/1 = off
GPIO.output(fan_pin,1) # cooling fan (max 1A)
GPIO.output(heater_pin,1) # heater unit (max 16A) 
GPIO.output(door_pin,1) # linear actuator for door (max 2A, H-bridge controlled)

#db connection setup
db = connect.getConnect()
r = db.cursor()

#if the environment around a RPi is 25 degrees, 
#the RPi in box/case reaches about 60 degrees Celsius. 
#Several components of the RPi is certified for 0-70 degrees, 
#such as the BCM2835 (700MHz SoC) and the LAN Chip.
#Safe temperature for Raspberry are considered between 0-70 
#degrees Celsius.

#init setup
heater_state = False;
fan_state = False;
high_temp = 35
low_temp = 2

#run/cool times
heater_run_time = datetime.timedelta(minutes = 5)
heater_cool_time = datetime.timedelta(minutes = 5)
fan_run_time = datetime.timedelta(minutes = 3)
fan_cool_time = datetime.timedelta(minutes = 1)

#Change fan state
def set_fan_state(new_state):
	if new_state != fan_state:
		if new_state:
			#High temp take action; fan on, open door
			#Check voltage / capacity (waiting for component)
        		turn_fan_on()
    		elif new_state is False:
    			#Turn off fan, close door
    			turn_fan_off();

#Change heater state		
def set_heater_state(new_state):
	if new_state != heater_state:
		if new_state:
			#Low temp take action; heater on
			#Check voltage / capacity (waiting for component)
			turn_heater_on()    		
    		elif new_state is False:
			# heating is finished turn off
			turn_heater_off();

#action methods	
def turn_heater_on():
	print("heater on!")
	GPIO.output(heater_pin,0)
	heater_state = True
    	r.execute('''INSERT INTO ptc (activity,temp) VALUES (%s,%s)''',('Heater On',read_temp()))
    	db.commit()

def turn_heater_off():
	print("heater off!")
	GPIO.output(heater_pin,1)
	heater_state = False
    	r.execute('''INSERT INTO ptc (activity,temp) VALUES (%s,%s)''',('Heater Off',read_temp()))
    	db.commit()
  
def turn_fan_on():
    	print("Fan on!")
	GPIO.output(fan_pin,0) 
    	fan_state = True
	r.execute('''INSERT INTO ptc (activity,temp) VALUES (%s,%s)''',('Fan On',read_temp()))
	db.commit

def turn_fan_off():
	print("fan off!")
	GPIO.output(fan_pin,1) 
    	fan_state = False
    	r.execute('''INSERT INTO ptc (activity,temp) VALUES (%s,%s)''',('Fan Off',read_temp()))
    	db.commit()
    	
				
				
def temperature_control_exec():

	temperature = read_temp();
	print(temperature);
	if temperature > low_temp and temperature < high_temp:
		print('temp ok!') #test purpose
		set_heater_state(False);
		set_fan_state(False)
	elif temperature >= high_temp:
		print('temp high!')
		set_heater_state(False);
		set_fan_state(True)
	else: #it's cold..
		print('temp low')
		set_heater_state(True);
		set_fan_state(False)

def main():
	
	while True:
		temperature_control_exec();
		time.sleep (120); #1 min 

if __name__ == '__main__':
	main()
