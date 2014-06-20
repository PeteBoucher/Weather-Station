#By Lars-Martin Hejll
#http://softwarefun.org
#windData.py
#collects wind speed and direction
#Using Weather Sensor Assembly p/n 80422 Imported by Argent Data Systems
#from sparkfun.com
# one RPS = 1.492 MPH of wind rfactor (datasheet)

from time import sleep
import time
import RPi.GPIO as GPIO, time, os
import MySQLdb
import connect

DEBUG = 0
counter = 0
finishtime = 0

rfactor = 1.492 #one RPS factor
samples = 5
speed = 0
directionPin = 18  #GPIO pin 
speedPin = 17 #GPIO pin
state = False

#setup GPIO's
GPIO.setmode(GPIO.BCM)
GPIO.setup(speedPin, GPIO.IN)
#direction wil be switched between in/out (RC circuit)

#db connection setup
db = connect.getConnect()
r = db.cursor()

#Direction by RC timing

#Test readings - benchmarking
#ideal numbers @ 20 deg. C
#North = 200 - 230
#NorthWest = 110 - 130
#West = 45 - 60
#SouthWest = 370 - 470
#South = 1830 - 1890
#SouthEast = 2300 - 3600
#East = 6500 - 6800
#NorthEast = 750 - 950


def getDirection ():
        reading = 0
        GPIO.setup(directionPin, GPIO.OUT)
        GPIO.output(directionPin, GPIO.LOW)
        time.sleep(0.1)

        GPIO.setup(directionPin, GPIO.IN)
        # This takes about 1 millisecond p/loop
        while (GPIO.input(directionPin) == GPIO.LOW):
                reading += 1
        #rough numbers to deal with temp. changes        
        if (reading > 189 and reading < 230):
                return ("North")
        elif (reading > 110 and reading < 190):
                return ("NorthWest")
        elif (reading > 45 and reading < 60):
                return ("West")
        elif (reading > 330 and reading < 470):
                return ("SouthWest")
        elif (reading > 1600 and reading < 2200):
                return ("South")
        elif (reading > 2300 and reading < 4500):
                return ("SouthEast")
        elif (reading > 5600 and reading < 6800):
                return ("East")
        elif (reading > 750 and reading < 950):
                return ("NorthEast")
        else:
                return(reading)

#Speed messurment
def getSpeed():
#    Loop some seconds (samples) and record pulses

	counter = 0 #numbers of interrupt
	# finishtime is right now (clock time) + 100 real seconds, not 
	# CPU cycles
	endTime = (int(time.time()) + samples)
	state = True
	while (int(time.time()) < endTime):
		if ( GPIO.input(speedPin) == False ):
			state = False #closed
		# wait for switch for open
		if ((state == False) and (GPIO.input(speedPin) == True)):
			# State is now open!
			state = True
			# count it!
			counter = counter + 1
#	counter is the total number of pulses during the sample time
#	speed in MPH
	speed = ((counter / samples)  * rfactor)
	return (speed)

def writeToDb(speed, direction):
        r.execute('''INSERT INTO wind (speed,direction) VALUES (%s,%s)''',(speed,direction))
        db.commit()	

def main():
    while True:
            speed = getSpeed()
            print (speed);
            direction = getDirection()
            print (direction);
            writeToDb(speed,direction)
            print("Writen to db");
    return 0

if __name__ == '__main__':
        main()

#By Lars-Martin Hejll
#http://softwarefun.org
#windData.py
