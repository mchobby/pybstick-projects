""" Mix CharlieWing class and MicroPython FrameBuffer """
from is31fl3731 import CharlieWing
import framebuf

class FramedCharlie( CharlieWing ):
	""" Class that embed CharliePlexing with FrameBuffer - 1 bit depth color"""
	def __init__( self, i2c ):
		super().__init__( i2c )
		self._intensity = 255
		# Créer un FrameBuffer
		# taille pour CharliePlex 15x7 (ADA3134) - 1bit_coleurr * 15 colonnes de 7 pixels = 1bit_color * 15 * 8 bits_par_column = 15 octets de stockage
		self.buf = bytearray(15)
		self.fb = framebuf.FrameBuffer( self.buf, self.width, self.height, framebuf.MVLSB ) # Monochrome couleur 1 bit, bit arrangés verticalement, 1ier bit vers le haut
		self.clear()       # the frame_buffer
		self.clear_frame() # Clear a Frame on the display
		self.paint_frame(frame=0, show=True ) # Send FrameBuffer to a frame and make it visible

	@property
	def framebuf( self ):
		return self.fb

	@property
	def intensity( self ):
		""" CharlieWing LED intensity (0..255) """
		return self._intensity

	@intensity.setter
	def intensity( self, value ):
		assert 0<= value <= 255
		self._intensity = value

	def clear( self ):
		self.fb.fill(0)

	def clear_frame( self, frame=0 ):
		self.frame( frame , show=False ) # select frame on CharlieWing
		self.fill(0) # Clear the frame (bypass the FrameBuffer)

	def paint_frame( self, frame=0, show=False ):
		""" Send the FrameBuffer data to a frame and possibly show it """
		# Transfer data
		for x in range(self.width):
			# utiliser le résultat du text écrit avec FrameBuffer
			bite = self.buf[x]
			for y in range(self.height):
				bit = 1 << y & bite
				# si bit > 0 alors fixer la luminosité
				if bit:
					self.pixel(x, y, self._intensity) # x,y,couleur=luminosité(0..255)
		# Afficher Frame ?
		if show:
			self.frame(frame, show=True)
