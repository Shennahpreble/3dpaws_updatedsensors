#!/usr/bin/python3
# Code to read the SparkFun Qwiic Soil Moisture Sensor
# Joseph Rener style - UCAR / COMET 3D-PAWS platform
# Sensor: SparkFun Qwiic Soil Moisture Sensor (default I2C address: 0x28)
# https://www.sparkfun.com/products/17731

import sys
sys.path.insert(0, '/home/pi/3d_paws/scripts/')
import time, helper_functions, datetime, os
import qwiic_soil_moisture_sensor

# Calibration values - adjust after field calibration
# Run sensor in dry air and in water to find your min/max
MOISTURE_MIN = 0     # raw reading in dry air
MOISTURE_MAX = 1023  # raw reading in water (fully wet)

def raw_to_percent(raw):
    """Convert raw moisture reading to percentage (0-100%)."""
    if raw <= MOISTURE_MIN:
        return 0.0
    elif raw >= MOISTURE_MAX:
        return 100.0
    else:
        return ((raw - MOISTURE_MIN) / (MOISTURE_MAX - MOISTURE_MIN)) * 100.0

# Set up sensor
try:
    sensor = qwiic_soil_moisture_sensor.QwiicSoilMoistureSensor()
    if not sensor.begin():
        print("ERROR: Soil moisture sensor not detected at 0x28. Check wiring.")
        sys.exit(1)
except Exception as e:
    print("ERROR: Could not connect to soil moisture sensor - " + str(e))
    sys.exit(1)

# Run
print("Soil Moisture Sensor - i2c address 0x28")

# Check if this is a test and set interval appropriately
test, samples, iterations = helper_functions.getTest()

# Add marker to file
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
filename = "/home/pi/data/tests/soil_moisture/soil_moisture_%s.dat" % now.strftime("%Y_%m_%d")
os.makedirs(os.path.dirname(filename), exist_ok=True)
marker = "----New Run Started at %s ----\n" % timestamp

try:
    with open(filename, "a") as f:
        f.write(marker)

    # Run once, or in test mode run every interval
    for i in range(0, iterations):
        try:
            total_moisture_raw = 0
            total_moisture_pct = 0

            for x in range(0, samples):
                sensor.read_moisture_level()
                raw = sensor.level
                pct = raw_to_percent(raw)

                # Debug print - remove once readings look correct
                print(f"Sample {x}: raw={raw}, pct={pct:.2f}%")

                total_moisture_raw += raw
                total_moisture_pct += pct
                time.sleep(1)

            # Calculate averages
            avg_raw = total_moisture_raw / samples
            avg_pct = total_moisture_pct / samples

            # Sanity check - flag bad readings
            if avg_raw <= 0:
                avg_raw = -999.99
                avg_pct = -999.99

            # Format output: moisture_raw, moisture_%
            line = "%.2f %.2f" % (avg_raw, avg_pct)
            print(line)

            if test:
                helper_functions.output(False, line, "test_soil_moisture")
            else:
                helper_functions.output(False, line, "soil_moisture")

        except Exception as e:
            helper_functions.handleError(e, "soil_moisture")

except Exception as e:
    helper_functions.handleError(e, "soil_moisture")
