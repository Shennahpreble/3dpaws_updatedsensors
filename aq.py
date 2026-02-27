#Test code for AQ sensor - Shennah Preble
#!/usr/bin/python3
# 3D-PAWS Air Quality (PMSA003I) continuous logging script
# Uses helper_functions for logging and error handling

import sys, time
sys.path.insert(0, '/home/pi/3d_paws/scripts/')
import board, busio, helper_functions
from adafruit_pm25.i2c import PM25_I2C

which_sensor = "air_quality"

# Initialize I2C and sensor
try:
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    sensor = PM25_I2C(i2c)
except Exception as e:
    helper_functions.handleError(e, which_sensor)
    sys.exit()

# Continuous loop
try:
    while True:
        try:
            aqdata = sensor.read()
            pm25 = aqdata["pm25 env"]  # Recommended PM2.5 reading

            # Print to terminal
            print("PMSA003I Sensor")
            print("PM2.5 (environmental): %.2f µg/m³" % pm25)
            print()

            # Log using helper_functions
            line = f"{which_sensor} {pm25:.2f}"
            helper_functions.output(False, line, "aq_log")  # logs to /home/pi/data/tests/aq_log/...

        except RuntimeError:
            print("Read error, retrying...")
            continue

        # Wait 10 seconds between readings
        time.sleep(10)

except Exception as e:
    helper_functions.handleError(e, which_sensor)
