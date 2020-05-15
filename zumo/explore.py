""" Using a Zumo Chassis + Ultrasonic + PYBStick to create a basic robot
    avoiding obstacle.

	* Press user A to start.
	* Red led will blink for 10 seconds before starting
	* Press user A again to stop the robot

	ultrasonic lib on https://wiki.mchobby.be/index.php?title=MicroPython-HC-SR04
	servozumo  lib on https://github.com/mchobby/pybstick-projects/tree/master/zumo

	See tutorial on https://github.com/mchobby/pybstick-projects/tree/master/zumo

	D.Meurisse for shop.mchobby.be
	11/05/2020, Domeu, Initial commit
"""
from machine import Pin
from pyb import Servo, Timer, LED, Switch
from ultrasonic import Ultrasonic
from servozumo import ServoZumo
from time import sleep
from urandom import choice, randint

# Untrasonic
TRIGGER_PIN = "S18"
ECHO_PIN = "S16"
# Zumo
RIGHT_SERVO = 4 # S10
LEFT_SERVO  = 3 # S8

sr04 = Ultrasonic( Pin(TRIGGER_PIN), Pin(ECHO_PIN) )
zumo = ServoZumo( left_servo = LEFT_SERVO, right_servo = RIGHT_SERVO )
sw = Switch()

# Wait user A to be pressed
while not sw.value():
	sleep( 0.100 )

# wait 10 secondes before start
for i in range(9):
	LED(1).on()
	sleep( 0.100 )
	LED(1).off()
	sleep( 1 )
# Final indicator
LED(1).on()
sleep(1)
LED(1).off()

try:
	while True:
		# if object detected
		while sr04.distance_in_cm() <= 25:
			# turn on right (positive speed) or left (negative speed) during a
			# random amount of time (400ms to 1.5s) to find an escape.
			zumo.right( speed = choice([-50,+50]), time_ms=randint(400,1500) )
		if not zumo.is_moving:
			zumo.speed( 80 ) # Move forward @ speed
		if sw.value():
			break
finally:
	zumo.stop()
