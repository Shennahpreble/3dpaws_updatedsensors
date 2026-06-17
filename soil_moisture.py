#!/usr/bin/python3
# Code to read the soil moisture and temperature sensor (Adafruit STEMMA / Qwiic capacitive)
# Based on 3D-PAWS sensor script style by Joseph Rener, UCAR
# Sensor: Adafruit STEMMA Soil Sensor (ATSAMD10 based, I2C, Seesaw protocol)
# Default I2C address: 0x36 (some boards/batches use 0x28 - confirm with i2cdetect)
# Developed for use with the 3D-PAWS weather station platform
# COMET / University Corporation for Atmospheric Research (UCAR)

import sys
sys.path.insert(0, '/home/pi/3d_paws/scripts/')
import time, helper_functions, datetime, os

# Sensor I2C registers (Seesaw protocol: module base + function byte)
MOISTURE_BASE   = 0x0F
MOISTURE_FUNC   = 0x10
TEMP_BASE       = 0x00
TEMP_FUNC       = 0x04

# Moisture calibration values (adjust after field calibration)
# ~200 = very dry, ~2000 = saturated/submerged
MOISTURE_MIN = 200    # raw reading in air (dry)
MOISTURE_MAX = 1800   # raw reading in water (wet)

def read_moisture(bus, address):
    """Read raw capacitance moisture value from sensor (Seesaw protocol)."""
    # Send the 2-byte command [base, function] together
    bus.write_i2c_block_data(address, MOISTURE_BASE, [MOISTURE_FUNC])
    # Seesaw moisture reads need time to settle - longer than the base seesaw delay
    time.sleep(0.5)
    # Read raw bytes back (no register byte needed on the read)
    data = bus.read_i2c_block_data(address, 0, 2)
    moisture_raw = (data[0] << 8) | data[1]
    return moisture_raw

def raw_to_percent(raw):
    """Convert raw moisture reading to percentage (0-100%)."""
    if raw <= MOISTURE_MIN:
        return 0.0
    elif raw >= MOISTURE_MAX:
        return 100.0
    else:
        return ((raw - MOISTURE_MIN) / (MOISTURE_MAX - MOISTURE_MIN)) * 100.0

def read_temperature(bus, address):
    """Read soil temperature in Celsius from the sensor's onboard thermistor (Seesaw protocol)."""
    bus.write_i2c_block_data(address, TEMP_BASE, [TEMP_FUNC])
    time.sleep(0.5)
    data = bus.read_i2c_block_data(address, 0, 4)
    temp_raw = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
    temp_c = temp_raw / 65536.0
    return temp_c

# Set up I2C
try:
    import smbus
    bus = smbus.SMBus(1)
    address = 0x28
    # Test connection by reading moisture register
    bus.write_i2c_block_data(address, MOISTURE_BASE, [MOISTURE_FUNC])
    time.sleep(0.5)
    _ = bus.read_i2c_block_data(address, 0, 2)
    sensor_ok = True
except Exception as e:
    sensor_ok = False
    print("ERROR: Could not connect to soil moisture sensor at 0x28 - " + str(e))
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
            total_temp         = 0

            for x in range(0, samples):
                raw  = read_moisture(bus, address)
                pct  = raw_to_percent(raw)
                temp = read_temperature(bus, address)

                # Debug print - remove once readings look correct
                print(f"Sample {x}: raw={raw}, pct={pct:.2f}, temp={temp:.2f}")

                total_moisture_raw += raw
                total_moisture_pct += pct
                total_temp         += temp
                time.sleep(1)

            # Calculate averages
            avg_raw  = total_moisture_raw / samples
            avg_pct  = total_moisture_pct / samples
            avg_temp = total_temp / samples

            # Sanity check - flag bad readings
            if avg_raw <= 0:
                avg_raw  = -999.99
                avg_pct  = -999.99
                avg_temp = -999.99

            # Format output: moisture_raw, moisture_%, soil_temp_C
            line = "%.2f %.2f %.2f" % (avg_raw, avg_pct, avg_temp)
            print(line)

            if test:
                helper_functions.output(False, line, "test_soil_moisture")
            else:
                helper_functions.output(False, line, "soil_moisture")

        except Exception as e:
            helper_functions.handleError(e, "soil_moisture")

except Exception as e:
    helper_functions.handleError(e, "soil_moisture")
