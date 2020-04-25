# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal

import machine
import pyb


run_pin = machine.Pin( "S22", machine.Pin.IN, machine.Pin.PULL_UP )

# run_pin = Low - Normal PYBStick operation
if run_pin.value() == 0:
	# Périphérique de stockage et port serie
	pyb.usb_mode('VCP+MSC') # act as a serial and a storage device
	# ne pas executer main.py
	pyb.main('nomain.py') # main script to run after this one
else:
	# Agir comme un clavier uniquement
	pyb.usb_mode('VCP+HID', hid=pyb.hid_keyboard) # Clavier + port série pour debug
	# pyb.usb_mode('VCP+HID', hid=pyb.hid_mouse) # Souris + port série pour debug
	pyb.main('keyb.py')
