""" Programme du Minuteur de brossage de dents

	Projet du travail de madenn disponible sur http://madenn.space/minuteur-automatique-pour-lavage-mains

	Voir GitHub du projet pour plus d'information:

	https://github.com/mchobby/pybstick-projects/tree/master/tooth-brushing-timer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/. """

from ws2812 import NeoPixel
from machine import Pin
from pyb import Timer
from ultrasonic import Ultrasonic
import time

TRIGGER_PIN = "S18" # HC-SR04
ECHO_PIN    = "S16"
NEOPIXEL_BUS = 1    # Ring NeoPixel
NEOPIXEL_LEDS= 24
BUZZER_PIN = "S22"  # Buzzer
BUZZER_TIMER = 1
BUZZER_CHANNEL = 3

LAVAGE_MS = 2 * 60 * 1000 # 2 Mins = 120 sec = 120 * 1000 ms
# LAVAGE_MS = 40000 # 40 sec

np = NeoPixel( spi_bus=NEOPIXEL_BUS, led_count=NEOPIXEL_LEDS, intensity=1 )
u  = Ultrasonic( TRIGGER_PIN, ECHO_PIN )

# Eteindre
np.fill( (0,0,0) )
np.write()

class MovingWheel:
	def __init__( self, np ):
		self.np = np
		self.wheel_pos = 0 # Current position in the moving Color Wheel
		self._fill_to   = self.np.n-1 # index of the last LED to light-up (remaining will be black)

	@property
	def fill_to( self ):
		return self._fill_to

	@fill_to.setter
	def fill_to( self, x ):
		assert 0 <= x < self.np.n
		self._fill_to = x

	def wheel_color( self, wheel_pos ):
		""" caculate color based on a color wheel.
		    Color are transistion r - g - b back r based on wheel_pos (0-255) """
		assert 0<= wheel_pos <= 255, "Invalid wheel_pos!"

		wheel_pos = 255 - wheel_pos
		if( wheel_pos < 85 ):
			return ( 255-(wheel_pos*3), 0, wheel_pos*3 )
		elif( wheel_pos < 170 ):
			wheel_pos -= 85
			return ( 0, wheel_pos*3, 255-(wheel_pos*3) )
		else:
			wheel_pos -= 170
			return ( wheel_pos*3, 255-(wheel_pos*3), 0 )

	def clear( self ):
		self.np.fill( (0,0,0) )
		self.np.write()
		self.wheel_pos = 0

	def update( self, wheel_step = 4 ):
		""" Cycle rainbow color over a series of NeoPixel """
		# Starting Rainbow color for the ribbon
		ruban_pos = self.wheel_pos

		# iterate Raibow color over the Ribbon
		for i in range( self.np.n-1, 0, -1 ):
			self.np[i] = self.wheel_color( ruban_pos )
			if i >= self._fill_to:  # Fill the remaining in black
				self.np[i] = (0,0,0)
			ruban_pos += wheel_step
			if ruban_pos > 255:
				ruban_pos = 0

		# next starting color
		self.wheel_pos += 1
		if self.wheel_pos > 255:
			self.wheel_pos = 0

		# update the ribbon
		self.np.write()

np_wheel = MovingWheel( np )

# Configurer les broches PWM pour la sortie sur buzzer
s22 = Pin(BUZZER_PIN) # Broche Y2 avec timer 8 et Channel 2
tim = Timer(BUZZER_TIMER, freq=3000)
ch = tim.channel(BUZZER_CHANNEL, Timer.PWM, pin=s22)
def play_freq( freq ):
	global ch
	if freq == 0:
		ch.pulse_width_percent( 0 )
	else:
		tim.freq( freq )
		ch.pulse_width_percent( 30 )

def tone( freq, duration ):
	play_freq( freq )
	time.sleep_ms( duration )
	play_freq( 0 )
	time.sleep_ms( 20 )

# === Routines ====================================

def animation_quarter( pause_ms = 1000 ):
	""" Indiquer les 4x 1/4 de bouche """
	for iQuarter in range(4): # les 4 / 4
		show_quarter( iQuarter )
		time.sleep_ms( pause_ms )

def show_quarter( quarter_no ):
	""" Light up a quarter between 0 & 3 """
	global np # NeoPixels
	couleur = (64,64,64) # Blanc (mi intensité)

	quarter_count = NEOPIXEL_LEDS // 4
	np.fill( (0,0,0) ) # Clear
	for iLed in range( quarter_count ):
		np[(quarter_count*(3-quarter_no))+iLed]=couleur
	np.write()

def lavage():
	""" Décompte de 40 secondes """
	global np, np_wheel # NeoPixels
	delay_ms  = LAVAGE_MS # delay for full cleaning
	quarter_ms= LAVAGE_MS // 4  # delay for a quarter

	quarter_display = [False, False, False, False] # Indicate if a quarter has already been showsed

	ref_ticks = time.ticks_ms()
	while (time.ticks_ms()-ref_ticks) < delay_ms:
		# Show the mounth quarter to proceed now
		quarter_no = (time.ticks_ms()-ref_ticks) // quarter_ms # 0..3
		if quarter_display[quarter_no] == False:
			# Blink the quarter
			for i in range( 4 ):
				show_quarter( quarter_no )
				time.sleep_ms(100)
				np.fill( (0,0,0) ) # Black
				np.write()
				time.sleep_ms(100)
			# Remember we showed it
			quarter_display[quarter_no] = True

		# Number of LEDs to light up
		try:
			iCount = int(NEOPIXEL_LEDS / (delay_ms / (time.ticks_ms()-ref_ticks)))
		except ZeroDivisionError: # peut arriver sur une plateforme super rapide
			iCount=0
		np_wheel.fill_to = (NEOPIXEL_LEDS-1)-iCount
		np_wheel.update()
		np.write()
	# Temps écoulé....
	np_wheel.clear()

def musique():
	# Tetris Theme based on http://www.jk-quantized.com/blog/2015/11/09/tetris-theme-song-using-processing
	tone( 2637, 300) # Mi
	tone( 1975, 150) # Si
	tone( 2093, 150) # Do
	tone( 2349, 300) # Re
	tone( 2093, 150) # Do
	tone( 1975, 150) # Di
	#
	tone( 1760, 300) # La
	tone( 1760, 150) # La
	tone( 2093, 150) # Do
	tone( 2637, 300) # Mi
	tone( 2349, 150) # Re
	tone( 2093, 150) # Do
	#
	tone( 1975, 450) # Si
	tone( 2093, 150) # Do
	tone( 2349, 300) # Re
	tone( 2637, 300) # Mi
	#
	tone( 2093, 300) # Do
	tone( 1760, 300) # La
	tone( 1760, 300) # La
	#tone( 1975, 150) # Si
	#tone( 2093, 150) # DO


# === Boucle principale ===========================
# Attendre action sur capteur ultrason
print("Pret")
while True:
	np[0] = (64,64,64) # Indique LED 0 pour assemblage
	np.write()
	if u.distance_in_cm() < 10:
		print("Detection")
		for i in range( 250, 0, -20 ):
			animation_quarter( pause_ms = i )
		print("Lavage Dents")
		lavage()
		print("Pret")
		musique()
