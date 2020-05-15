""" Small class to propel the Zumo Chassis with Servo-Controller DC Motor

	See tutorial on https://github.com/mchobby/pybstick-projects/tree/master/zumo

	D.Meurisse for shop.mchobby.be
	11/05/2020, Domeu, Initial commit
"""
from time import sleep_ms
from pyb import Servo

class ServoZumo:
	""" A mini class to drive a Zumo Chassis (POL-1418) + DFRobot Servo motor (DFR0399) """
	def __init__( self, left_servo, right_servo ):
		# This motor requires a timer @ 500 Hz so modify the timer(5) used by Servo from 50 HZ to 500 Hz
		self._left  = Servo( left_servo )
		#self.left.calibration(500, 2500, 1500, 2500, 2500)
		self._right = Servo( right_servo )
		#self.right.calibration(500, 2500, 1500, 2500, 2500)
		self._moving = False
		self.stop()

	@property
	def is_moving( self ):
		return self._moving

	def stop( self ):
		self._right.speed( 0 )
		self._left.speed( 0 )
		self._moving = False

	def speed( self, speed ):
		""" Speed from -100 (backward) to +100 (forward) """
		self._right.speed( -1*speed )
		self._left.speed( speed )
		self._moving = True

	def right( self, speed, time_ms=None ):
		""" Turn right @ given speed. if time_ms is given, it stop after the given time """
		self._right.speed( speed )
		self._left.speed( speed )
		self._moving = True
		if time_ms:
			sleep_ms( time_ms )
			self.stop()

	def left( self, speed, time_ms=None ):
		""" Turn left @ given speed. if time_ms is given, it stop after the given time """
		self.right( -1*speed, time_ms )
