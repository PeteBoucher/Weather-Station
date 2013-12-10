import os
import glob
import time
import MySQLdb
import re

#By Lars-Martin Hejll
#http://softwarefun.org

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
#replace ***** with your sensor id
device_folder1 = glob.glob(base_dir + '28-00000*******')[0]
device_file1 = device_folder1 + '/w1_slave'
device_folder2 = glob.glob(base_dir + '28-00000*******')[0]
device_file2 = device_folder2 + '/w1_slave'

def read_temp_raw2():
        e = open(device_file2, 'r')
        lines2 = e.readlines()
        e.close()
        return lines2

def read_temp():
#-62 is "busy" signal from temp sensor
        result = None
        res = '10000' #init value

        while result is None:

            if result is None:
                time.sleep(1)
                #regex to grab number negativ
                result = re.search('t=(\d+[\+|\-]{1}|[\-|\+]{1}\d+)',str(read_temp_raw2()))
            if result is None:
            	#regex to grab number positiv
                result = re.search('t=(\d+)',str(read_temp_raw2()))
            if result:
            #if busy/faulty value is taken, set result=None
                if result.group(1) == '-62':
                    result = None
                    time.sleep(1)

        res=result.group(1)
        temp = float(res) / 1000;
        return temp

def read_temp_raw1():
        e = open(device_file1, 'r')
        lines1 = e.readlines()
        e.close()
        return lines1

def read_temp2():
#-62 is "busy" signal from temp sensor
        result = None
        res = '10000' #init value

        while result is None:
            if result is None:
                time.sleep(1)
                #regex to grab number negativ
                result = re.search('t=(\d+[\+|\-]{1}|[\-|\+]{1}\d+)',str(read_temp_raw1()))
            if result is None:
                #regex to grab number positiv
                result = re.search('t=(\d+)',str(read_temp_raw1()))
            if result:
            #if busy/faulty value is taken, set result=None
                if result.group(1) == '-62':
                    result = None
                    time.sleep(1)

        res=result.group(1)
        temp = float(res) / 1000;
        return temp

#db connection    
db = MySQLdb.connect("host","user","pass","db")
r = db.cursor()

t1 = read_temp()
t2 = read_temp2()
dif = t2-t1
#write to mySql db
r.execute('''INSERT INTO Table (col,col,col) VALUES (%s,%s,%s)''',(t1,t2,dif))
db.commit()
print("Temp1 + Temp2 + diff is writen to database @ host")
        