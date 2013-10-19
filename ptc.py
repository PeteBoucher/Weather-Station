import os
import glob
import time
import MySQLdb
import RPi.GPIO as GPIO

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
#setup GPIO's for FAN(cooling 12) and HEATER (18)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

#setup for tempsensors
base_dir = '/sys/bus/w1/devices/'
device_folder1 = glob.glob(base_dir + '28-00000384c25d')[0]
device_file1 = device_folder1 + '/w1_slave'
device_folder2 = glob.glob(base_dir + '28-00000384c1bb')[0]
device_file2 = device_folder2 + '/w1_slave'

def read_temp_raw2():
        e = open(device_file2, 'r')
        lines2 = e.readlines()
        e.close()
        return lines2

def read_temp(): #external

        lines2 = read_temp_raw2()
        while lines2[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines2 = read_temp_raw2()

        equals_pos2 = lines2[1].find('t=')
        if equals_pos2 != -1:
                temp_string2 = lines2[1][equals_pos2+2:]


                temp_c_out = float(temp_string2) / 1000.0

                return temp_c_out

def read_temp_raw1():
        e = open(device_file1, 'r')
    	lines1 = e.readlines()
        e.close()
        return lines1

def read_temp2(): #internal

        lines1 = read_temp_raw1()
        while lines1[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines1 = read_temp_raw1()

        equals_pos1 = lines1[1].find('t=')
        if equals_pos1 != -1:
                temp_string1 = lines1[1][equals_pos1+2:]


                temp_c_out = float(temp_string1) / 1000.0

                return temp_c_out
#set values high = off
GPIO.output(18,1)
GPIO.output(12,1)

#db connection setup
db = MySQLdb.connect("host","user","pass","db")
r = db.cursor()

#loop to check temp and take action as necessary, RPi safe temp = 0-70 C

while True:
        if read_temp2() >1:
                if read_temp2() < 25:
                        print("temp is good!")
                        print(read_temp2())
                        print("Temp is good: 1-25C")
                        time.sleep(300)
        if read_temp2() >25:
                GPIO.output(12,0)
                print(read_temp2())
                print("High temp, turning ON fan")
                r.execute('''INSERT INTO ptc (activity,temp) VALUES (%s,%s)''',('Fan ON',read_temp2()))
                db.commit()
                time.sleep(300)
                print("5min fan time past, turning OFF fan")
                GPIO.output(12,1)

        if read_temp2() < 1:
                print(read_temp2())
                print("low temp < 1 heater on for 5min")
                GPIO.output(18,0)
                r.execute('''INSERT INTO ptc (activity,temp) VALUES (%s,%s)''',('Heater ON',read_temp2()))
                db.commit()
                time.sleep(300)
                print("50/50 duty cycle 5 min heater off (safty for cabels)")
                GPIO.output(18,1)
                time.sleep(300)

        print("New check (every 5 min)")
