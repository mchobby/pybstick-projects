""" Create a ChaliePlexing Mini-Clock based on PCF8523 RTC, 15x7 ChaliePlexing
	FeatherWing and a PYBStick under MicroPython.

	See projet details @ https://github.com/mchobby/pybstick-projects/tree/master/charlie-clock
"""

from machine import I2C
from pcf8523 import PCF8523
from fcharlie import FramedCharlie
import time

FONT = { 0: [0b01111111,0b01000001,0b01111111],
		 1: [0b00000000,0b00000010,0b01111111],
		 2: [0b01111001,0b01001001,0b01001111],
		 3: [0b01001001,0b01001001,0b01111111],
		 4: [0b00001111,0b00001000,0b01111111],
		 5: [0b01001111,0b01001001,0b01110001],
		 6: [0b01111111,0b01001001,0b01111001],
		 7: [0b00000001,0b00000001,0b01111111],
		 8: [0b01111111,0b01001001,0b01111111],
		 9: [0b01001111,0b01001001,0b01111111] }

INTENSITY = 20

class ClockCharlie( FramedCharlie ):
	""" Specialized class for the DIGIT BASED clock """

	def draw_digit( self, value, position ):
		""" routine that draws a digit (0..9) at a given position (0..3) """
		x_start = position * 4
		_font   = FONT[value] # value=4 -> [0b00001111,0b00001000,0b01111111],
		for col in range( len(_font) ):
			for y in range( 0, 8 ): # Only the 7 firsts bits
				bit_weight = pow( 2, y )
				if _font[col] & bit_weight == bit_weight:
					self.fb.pixel( x_start+col, y, 1 ) # Draw the Pixel


# PYBStick - S3=sda, S5scl
i2c = I2C(1)
rtc = PCF8523( i2c )
disp= ClockCharlie( i2c ) # Display
disp.intensity = INTENSITY

frame = 0 # Alternate between frames to avoid flickering
while True:
	_now = rtc.datetime
	_dt  = time.localtime(_now) # Year, month, day, hour, min, sec, weekday, yearday
	hh = _dt[3]
	mm = _dt[4]
	ss = _dt[5]
	# Clear the Frame Buffer
	disp.clear()
	disp.draw_digit( hh//10, 0 )
	disp.draw_digit( hh%10 , 1 )
	disp.draw_digit( mm//10, 2 )
	disp.draw_digit( mm%10 , 3 )
	# blink a pixel every seconds... pixel goes down when minutes passing by
	disp.framebuf.pixel( 7, ss//9, (ss%2 == 1) )
	# Send FrameBuffer to display + Show
	disp.clear_frame( frame ) # Also erase previous drawing
	disp.paint_frame( frame, show=True )
	# change over the frame to use
	frame = 0 if frame else 1
