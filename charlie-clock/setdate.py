""" MicroPython driver for the PCF8523 RTC over I2C.

	Set the RTC time to a fixed date

	Dominique Meurisse for MCHobby.be - initial portage

"""

from machine import I2C
from pcf8523 import PCF8523
import time

# PYBStick - S3=sda, S5scl
i2c = I2C(1)

rtc = PCF8523( i2c )

# Year: 2020, month: 6, day: 22, hour: 0, min: 14, sec: 6, weekday: 0 (monday), yearday: 174
rtc.datetime = (2020, 6, 22, 0, 14, 6, 0, 174)
