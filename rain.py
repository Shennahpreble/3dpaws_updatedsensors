#!/usr/bin/python3
# Code to control the tipping bucket rain gauge. Write observations to disk
# Computes a 1 minute geometric average
# Paul A. Kucera, Ph.D. and Joseph Rener
# UCAR
# Boulder, CO USA
# Email: pkucera@ucar.edu and jrener@ucar.edu
# Developed at COMET at University Corporation for Atmospheric Research and the Research Applications Laboratory at the National Center for Atmospheric Research (NCAR)

import sys
sys.path.insert(0, '/home/pi/3d_paws/scripts/')
import RPi.GPIO as GPIO, time, helper_functions, datetime, os 

# Set rest interval based on if we're testing or not
test, rest, iterations = helper_functions.getTest()

# Rainfall Accumulation in mm per bucket tip (TB3 Specs)
CALIBRATION = 0.2

# Identify the GPIO pin for the rain gauge
PIN = 2

# Start sensor
GPIO.setmode(GPIO.BCM)  
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variable to keep track of how much rain
rain = 0.0

# Call back function for each bucket tip
def tipped(channel):
	global rain
	rain = rain + CALIBRATION
				
# Register the call back for pin interrupts
GPIO.add_event_detect(PIN, GPIO.FALLING, callback=tipped, bouncetime=300)

print("Rain (tipping bucket) Sensor")

#Updated - add marker to file
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
filename = "/home/pi/data/tests/rain/rain_%s.dat" % now.strftime("%Y_%m_%d")
os.makedirs(os.path.dirname(filename),exist_ok=True)

marker = "----New Run Started at %s ----\n" %timestamp

try:
    with open(filename, "a") as f:
        f.write(marker)
#End main sections of additions 


# Run once... or if in test mode, run every 10 seconds during the interval
    for x in range (0, iterations):
        time.sleep(rest)
        try:
		# Handle script output
            line = "%.2f" % (rain)
            print(line)
            if test:
                helper_functions.output(False, line, "test_rain")
            else:
                helper_functions.output(False, line, "rain")

		# Reset rain
            if test:
                rain = 0.0
            else:
                break

        except Exception as e:
            helper_functions.handleError(e, "rain")
            GPIO.cleanup()
            break
except Exception as e:
        helper_functions.handleError(e, "rain")
        GPIO.cleanup()