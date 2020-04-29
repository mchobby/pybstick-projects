""" Display Pyboard statistic on the OLED screen.

	ssd1306 lib on https://raw.githubusercontent.com/micropython/micropython/master/drivers/display/ssd1306.py
	see wiring @ https://github.com/mchobby/pybstick-projects/tree/master/oled-stat
"""

from machine import I2C, Pin
from ssd1306 import SSD1306_I2C

from os import statvfs
from time import sleep
import gc

# WARNING: sur la pyboard, le pilote ssd1306 est écrit pour machine.I2C (et pas pour pyb.I2C)
#          et le bus I2C doit être instancier avec une configuration spécifique des broches.
#          Voir le topic https://forum.micropython.org/viewtopic.php?f=6&t=4663
# Pyboard: SDA sur Y9, SCL sur Y10. Voir raccordement NCD sur https://github.com/mchobby/pyboard-driver/tree/master/NCD
#

class MPStat:
	def __init__( self ):
		self.pscl = Pin('S5', Pin.OUT_PP)
		self.psda = Pin('S3', Pin.OUT_PP)
		self.i2c = I2C(scl=self.pscl, sda=self.psda)
		self.lcd = SSD1306_I2C( 128, 32, self.i2c )

		self.lcd.rect(0,0,128,32,1) # Cadre blanc
		self.lcd.show()  # Afficher!

	def update( self, ram=True ):
		# read and display stat
		stat = statvfs('/flash') # Internal Flash
		blocksize = stat[0]
		fragsize = stat[1]
		fragfs = stat[2]
		freeblocks = stat[3]
		fs_size = fragfs*fragsize / 1024 # In KB
		free_size = blocksize*freeblocks / 1024 # In Kb

		# Clear frame buffer
		self.lcd.fill_rect( 1,1, 126, 30, 0 ) # Clear the content
		# Show FS usage
		self.lcd.text( "FS: %2i/%2i Kb" % (fs_size-free_size,fs_size), 6, 4, 1)

		# Display Progress bar
		self.lcd.rect( 5, 15, 118, 14, 1 ) # empty frame
		fill_ratio = (fs_size-free_size)/fs_size
		self.lcd.fill_rect( 5, 15, int(118 * fill_ratio), 14, 1 )
		if fill_ratio < 0.50:
			self.lcd.text( '%i %%' % (fill_ratio*100), 71,17, 1 )
		else:
			self.lcd.text( '%i %%' % (fill_ratio*100), 10,17, 0 )

		# Display RAm instead of progress bar
		if ram:
			self.lcd.fill_rect( 5, 15, 118, 14, 0 ) # empty frame
			self.lcd.text( "RAM: %4.1f Kb" % (gc.mem_free()/1024), 6, 17, 1)

		self.lcd.show()

mpstat = MPStat()
mpstat.update( ram=False )
sleep(1)
mpstat.update( ram=True )

def update( ram=True ):
	""" Easy update of the display """
	global mpstat
	mpstat.update( ram )
