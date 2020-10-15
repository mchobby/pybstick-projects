# SMS Relay - Controler un relais / relever la température à distance par SMS
#
# Debug may be activated to see all messages exchanges with the modem
#
# See Project: https://github.com/mchobby/pybstick-projects/tree/master/sms-relay
#
from machine import UART, Pin
from smodem import SimModem, AS_READY, CommandError
from config import PIN_CODE, MASTER_PHONE
import time
from onewire import OneWire
from ds18x20 import DS18X20

# GSM : UART and PowerPin to SIM Module
# Will be reconfigured by SimModem
uart = UART(1) # X9, X10 on Pyboard
pwr = Pin('S18') # Power On Pin, use "Y3" for Pyboard
# RELAY & OneWire bus
RELAY_PIN = 'S26'
ONEWIRE_PIN = 'S23'

m = SimModem( uart, pwr_pin = pwr, pin_code=PIN_CODE )
m.debug = False

relay = Pin( RELAY_PIN, Pin.OUT, value=False  )

bus = OneWire( Pin('S23') )
ds = DS18X20( bus )
roms = ds.scan()

def get_temp():
	""" Get the temperature from the DS18B20 """
	global ds
	global roms
	ds.convert_temp()
	time.sleep_ms(750)
	return ds.read_temp( roms[0] ) # Get the temp value for the first rom

def execute( sender, cmd ):
	""" Just execute the various command (uppercase,striped) """
	global relay
	global m

	if cmd=='ON':
		relay.value( 1 )
	elif cmd=='OFF':
		relay.value( 0 )
	elif cmd=='STATUS':
		m.send_sms( sender, 'Relay is %s\rTemp: %5.2f deg' % ('ON' if relay.value() else 'off', get_temp()) )
	else:
		print( 'Command %s not supported!' % cmd )
		m.send_sms( sender, 'Invalid command %s !' % cmd )


print( 'Activate modem' )
r = m.activate() # Activate / reinit the Modem
print( 'Modem initialized!' )

# Wait Modem to be ready
m.wait_for_ready()

# Empty the SMS Store
retries = 0
while True:
	try:
		print( 'Open SMS store - attempt %i' % retries )
		stored = m.stored_sms
		break
	except CommandError as err:
		retries += 1
		if retries > 5:
			raise # We end the script HERE
		else:
			print( 'pausing 20sec')
			time.sleep(20)

print( 'Empty SMS store' )
for id in stored:
	print( "  Drop sms %i" % id )
	m.delete_sms( id )

# Here how to wait for SMS and read them
print( 'Wait for SMS...' )
while True:
	m.update()
	if m.has_sms:
		for id in m.rec_sms:
			sms = m.read_sms( id, delete=True ) # Delete it from the SMS Store
			print( 'Sender : %s' % sms.sender )
			print( 'Time   : %s' % sms.send_date )
			for line in sms.lines:
				print( line )
				execute( sms.sender, line.strip().upper() ) # process the command in the line
			print( '-'*40 )

print( "That's all folks" )
