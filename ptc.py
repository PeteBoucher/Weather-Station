import os
import glob
import time
import MySQLdb
import RPi.GPIO as GPIO

#temp from 2x BS18B20 sensors

#initialize device
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
#now the "one-wire" device is visible at /sys/bus/w1/devices (base_folder)
#"one-wire" device pin is GPIO4 (physical pin number 7)
#setup GPIO's for FAN cooling 12 (ph) and HEATER 18 (ph) 22 linear actuator
GPIO.setup(12, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

#setup for temp sensors
#w1 is a virtual folder

device_base_folder = '/sys/bus/w1/devices/'
device_folder_1 = glob.glob(device_base_folder + '28-00000384c1bb')[0]
device_file_1 = device_folder_1 + '/w1_slave'
    
#get raw temp from sensor        
def read_temp_raw_1():
	try:
        e = open(device_file_1, 'r')
        raw_1 = e.readlines()
        e.close()
        except ValueError:
        	print("no sensor found")
        return raw_1
		#returns an array of sensor data (BS18B20)
		#with the temp from sensor in index(1).
		
def read_temp_1():

        raw_1 = read_temp_raw_1()
        
        #raw array format: ['73 00 4b 46 7f ff 0d 10 7c : crc=7c YES\n', '73 00 4b 46 7f ff 0d 10 7c t=14800\n']
        #actual value= 14800 => 14.800 C
        
        #searching for pattern 't=' in tabel position 2 (index 1)
        # normal setup: "t=14800" this wil reflect the temperatur 14.8 C
        
        position = raw_1[1].find('t=')
        if position != -1: #not found
                temp_string1 = raw_1[1][position+2:] #format => 14800
                temp_c_out = float(temp_string1) / 1000.0 #format => 14800
  		else:
  				temp_c_out = -1
  				error1()
  					
        return temp_c_out

#errors
def error1():
	raise RuntimeError('no sensor data!')
                
#init setup, set values high/1 = off
GPIO.output(18,1) # heater unit (max 16A)
GPIO.output(12,1) # cooling fan (max 1A)
GPIO.output(22,1) # linear actuator for door (max 2A, H-bridge controlled)

#db connection setup
db = MySQLdb.connect("host","user","pass","db")
r = db.cursor()

#loop to check temp and take action as necessary, RPi safe temp = 0-70 C

while True:
        if read_temp_1() >1:
                if read_temp_1() < 25:
                		#normal temp, no action
                        time.sleep(300) #wait 5 min for new check
                        else:
        						if read_temp_1() >25:
        							#High temp take action; fan on 5min, open door
        							GPIO.output(22,0)
                					GPIO.output(12,0)
                					#write action to database
                					r.execute('''INSERT INTO ptc (activity,temp) VALUES (%s,%s)''',('Fan ON',read_temp_1()))
                					db.commit()
                					time.sleep(300)
                					# 5min fan time past, fan off
                					GPIO.output(12,1)
                					GPIO.output(22,1)

        						if read_temp_1() < 1:
                					# low temp take action; heater on 5min
                					GPIO.output(18,0)
                					#write action to database
                					r.execute('''INSERT INTO ptc (activity,temp) VALUES (%s,%s)''',('Heater ON',read_temp_1()))
                					db.commit()
                					time.sleep(300)
                					#5min heat time past, heater off
                					GPIO.output(18,1)
                					#50/50 duty cycle 5 min heater off (safty for cabels)
                					time.sleep(300)

    #New check (every 5 min)
