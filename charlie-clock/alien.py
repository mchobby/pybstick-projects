""" Create a ChaliePlexing Alien Mini-Clock based on PCF8523 RTC, 15x7 ChaliePlexing
	FeatherWing and a PYBStick under MicroPython.

	See projet details @ https://github.com/mchobby/pybstick-projects/tree/master/charlie-clock
"""

from machine import I2C
from pcf8523 import PCF8523
from fcharlie import FramedCharlie
import time

FONT = { 0: [0b01111111,0b01000001,0b01000001,0b01000001,0b01000001,0b01000001,0b01111111],
		 1: [0b01111111,0b01000000,0b01000000,0b01000111,0b01000001,0b01000001,0b01111111],
		 2: [0b00000000,0b00011100,0b00000000,0b00001000,0b00000000,0b00011100,0b00000000],
		 3: [0b00001111,0b00011000,0b00011000,0b00010000,0b00010010,0b01110000,0b00011000],
		 4: [0b01111111,0b01000000,0b01000000,0b01000111,0b01000001,0b01000001,0b01111111],
		 5: [0b00011110,0b00010010,0b01010010,0b01011110,0b00100001,0b00000001,0b00000000],
		 6: [0b00000000,0b00111111,0b01000001,0b01001001,0b01000011,0b01110000,0b00000000]  }

INTENSITY = 20

class AlienCharlie( FramedCharlie ):
	""" Specialized class for the ALIEN BASED CARACTERS clock """

	def draw_alien_digit( self, value, position, inverted=False):
		""" routine that draws a Alien digit (0..6) at a given position (0..1) """
		x_start = position * 8
		_font   = FONT[value]
		_data   = None
		for col in range( len(_font) ):
			_data = _font[col]
			if inverted:
				_data = 0xFF ^ _data
			for y in range( 0, 8 ): # Only the 7 firsts bits
				bit_weight = pow( 2, y )
				if _data & bit_weight == bit_weight:
					self.fb.pixel( x_start+col, y, 1 ) # Draw the Pixel

i2c = I2C(1)
rtc = PCF8523( i2c )
disp= AlienCharlie( i2c ) # Display
disp.intensity = INTENSITY

frame = 0
while True:
	_now = rtc.datetime
	_dt  = time.localtime(_now)
	hh = _dt[3]
	mm = _dt[4]
	ss = _dt[5]
	disp.clear()

	if hh==0:
		_digit = 0
	elif hh%6 == 0:
		_digit = 6
	else:
		_digit = hh%6
	hh12 = hh if hh<= 12 else hh-12
	disp.draw_alien_digit( _digit, 0, hh12>6 ) # Invert digit iffrom 7 to 12H.

	five_min = mm//5 # value from 0 to 11
	if five_min==0:
		_digit = 0
	elif five_min%6 == 0:
		_digit = 6
	else:
		_digit = five_min%6
	disp.draw_alien_digit( _digit, 1, five_min>6 )
	_pos = (mm%5)*60+ss
	_pos = int( _pos / (5*60) * 7 )
	disp.framebuf.pixel( 7, _pos, (ss%2 == 1) )
	disp.clear_frame( frame ) # Also erase previous drawing
	disp.paint_frame( frame, show=True )
	frame = 0 if frame else 1
