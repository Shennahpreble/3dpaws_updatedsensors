#Test code for PMSA0031 air quality sensor - Shennah Preble

#!/usr/bin/python3

import sys, time
sys.path.insert(0, '/home/pi/3d_paws/scripts/')
import board, busio, helper_functions
from adafruit_pm25.i2c import PM25_I2C

which_sensor = "air_quality"

try:
    # I2C at 100kHz (important!)
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    sensor = PM25_I2C(i2c)

except Exception as e:
    helper_functions.handleError(e, which_sensor)
    sys.exit()

try:
    variables = helper_functions.getVariables()
    test_mode = variables[0]
    interval = helper_functions.getCron()[0]
    iterations = (interval * 6) - 1

    for x in range(0, iterations):

        try:
            aqdata = sensor.read()
            pm25 = aqdata["pm25 env"]

            print("PMSA003I Sensor")
            print("PM2.5 (env): %.2f µg/m³" % pm25)
            print()

            line = f"{which_sensor} {pm25:.2f}"
            helper_functions.output(False, line, "test_air_quality")

        except RuntimeError:
            print("Read error, retrying...")
            continue

        if test_mode == "true":
            time.sleep(10)
        else:
            break

except Exception as e:
    helper_functions.handleError(e, which_sensor)
