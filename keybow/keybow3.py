""" Keybow mini-keyboard sending custom key code to your computer.
    Use an AZERTY keymap for the Keyboard.

	Do not forgot to change the boot.py file to activate USB HID support with
    pyb.usb_mode('VCP+HID', hid=pyb.hid_keyboard)

	usbhid lib on https://github.com/mchobby/pyboard-driver/tree/master/usbhid
	example sourced from usbhid
"""
# CTRL-C : Wire X9 to the ground via a Push-Button
# CTRL-V : Wire X10 to the ground via a Push-Button
from machine import Pin, SPI
from pyb import LED
import pyb
from kmap_frbe import kmap, CTRL, SHIFT, CTRL_RIGHT, SHIFT_RIGHT
from usbhid import *
from dotstar import DotStar
from time import sleep_ms

hid = pyb.USB_HID()
spi = SPI( sck=Pin("S23",Pin.OUT), mosi=Pin("S19",Pin.OUT), miso=Pin("S21",Pin.OUT) )
leds = DotStar( spi, 3 )
leds.fill( (80,80,80) )

class Btn():
    """ Button with software debouncing. Count the number of time a button is
        pressed. Have a reject_ms to reject several button within a given
        timelapse. """
    def __init__( self, pin, reject_ms=200 ):
        self.pin = pin
        self.counter = 0
        self.last_millis = 0
        self.reject_ms = 200
        self.state = pin.value()

    def update( self ):
        """ Compute the state of the button. Call it as ofter as possible """
        _current = self.pin.value()
        if _current != self.state:
            sleep_ms( 20 )
            if self.pin.value()!=_current:
                return
            # count on raising edge
            if self.state==False and _current==True:
                if (pyb.millis()-self.last_millis)<self.reject_ms:
                    return
                self.counter += 1
                self.last_millis = pyb.millis()
            self.state = _current

    @property
    def has_pressed( self ):
        """ Check if the button as been pressed somehow """
        if self.counter > 0:
            self.counter = 0 # reset the counter
            return True
        return False


pin_left = Pin("S12", Pin.IN, Pin.PULL_UP)
btn_left = Btn( pin_left )

pin_middle = Pin("S10", Pin.IN, Pin.PULL_UP)
btn_middle = Btn( pin_middle )

pin_right = Pin("S8", Pin.IN, Pin.PULL_UP)
btn_right = Btn( pin_right )

pin_mode = Pin("S11", Pin.IN, Pin.PULL_UP)
btn_mode = Btn( pin_mode )

btns = [btn_left,btn_middle,btn_right,btn_mode]
mode = 0
# Associate Mode with color for buttons and defintion for each key
configs = {
   0: { 'color':(64,0,0), # red color for KeyBow buttons
        'keys' : [ (btn_left   , 'c', [CTRL] ), # Associate button with key and modifiers
                 (btn_middle, 'v', [CTRL] ),
                 (btn_right , 'a', [CTRL] ) ]
       },
   1: { 'color':(0,64,0), # green color for KeyBow buttons
        'keys' : [ (btn_left   , 'c', [CTRL_RIGHT,SHIFT_RIGHT] ), # Associate button with key and modifiers
                   (btn_middle, 'v', [CTRL_RIGHT,SHIFT_RIGHT] ),
                   (btn_right, 'v', [CTRL] )    ]
       },
   2: { 'color':(0,0,64), # blue color for KeyBow buttons
        'keys' : [ (btn_left  , [ ('u',[SHIFT,CTRL],200), ('2',[None],200), ('1',[None],200),('2',[],200),('6',[],200), '\r' ] ), # Unicode sequence for Omega (Linux)
                   (btn_middle, '?', None ),
                   (btn_right , '?', None )    ]
       }
}

def get_key_config( mode, btn_ref ): # Returns the key definition to send to the
    keys = configs[mode]['keys']
    for item in keys: # each (btn_right, 'v', [CTRL] )
        if item[0] == btn_ref:
            return item
    return None

# Switch RED LED on = Keyboard is running
LED(1).on()
leds.fill( configs[mode]['color'] )
try:
    # Reading the keys
    while True:
       # Update buttons
       for btn in btns:
           btn.update()
       if btn_mode.has_pressed:
           mode += 1
           if not( mode in configs ):
               mode = 0
           leds.fill( configs[mode]['color'])
           continue

       for btn in btns:
           if btn.has_pressed:
               key_config = get_key_config( mode, btn )
               if key_config:
                   leds.fill( (0,0,0) )
                   if type(key_config[1]) is str: # a single char + modifier
                       sendchr( key_config[1], hid, kmap, modifiers=key_config[2] )
                   elif type(key_config[1]) is list: # a sequence
                       sendseq( key_config[1], hid, kmap )
                   else:
                       raise ValueError( 'Invalid type %s for key_config data' % type(key_config) )
                   sleep_ms( 50 )
                   leds.fill( configs[mode]['color'])

       #if btn_copy.has_pressed:
       #   sendchr( 'c', hid, kmap, modifiers=[CTRL] )
       #btn_paste.update()
       #if btn_paste.has_pressed:
       #   sendchr( 'v', hid, kmap, modifiers=[CTRL] )
except:
    LED(1).off() # Switch of Keyboard is no more running
    LED(4).on()  # Light blue LED in case of trouble
    raise #forward exception
