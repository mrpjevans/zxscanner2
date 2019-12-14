#
# ZX Raspberry Keyboard Scanner v5
# @mrpjevans mrpjevans.com 2019
# MIT License (https://opensource.org/licenses/MIT) see LICENSE
#

import time, sys, os
from gpiozero import DigitalInputDevice, DigitalOutputDevice, Button

# KB1 (BCOM GPIO pins)
dataLines = [26,19,13,6,5]

# KB1 (BCOM GPIO pins)
addressLines = [25,24,23,22,27,18,17,4]

# The ZX Spectrum Keyboard Matrix (Mapped to modern keyboard)
keys = [
	['5','4','3','2','1'],
	['T','R','E','W','Q'],
	['G','F','D','S','A'],
	['6','7','8','9','0'],
	['B','N','M','LEFTCTRL','SPACE'],
	['H','J','K','L','ENTER'],
	['V','C','X','Z','LEFTSHIFT'],
	['Y','U','I','O','P']
]

# Function key mode
funcKeys = [
	['LEFT','F4','F3','F2','F1'],
	['T','R','E','W','Q'],
	['G','F','D','S','A'],
	['DOWN','UP','RIGHT','9','ESC'],
	['B','N','M','LEFTCTRL','SPACE'],
	['H','J','K','L','ENTER'],
	['V','C','X','Z','LEFTSHIFT'],
	['Y','U','I','O','P']
]

# Track keypresses so we can support multiple keys
keyTrack = [
	[False, False, False, False, False],
	[False, False, False, False, False],
	[False, False, False, False, False],
	[False, False, False, False, False],
	[False, False, False, False, False],
	[False, False, False, False, False],
	[False, False, False, False, False],
	[False, False, False, False, False]
]

# Keyboard mode and reset button
modeButton = Button(21)
buttonTime = 0

# 0 = Spectrum, 1 = Function Keys
keyboardMode = 0

# KB1 (BCOM GPIO pins)
dataLineIds = [26,19,13,6,5]
dataLines = [];

# KB2 (BCOM GPIO pins)
addressLineIds = [25,24,23,18,22,27,17,4]
addressLines = []

# Set all data lines to input
for dataLineId in dataLineIds:
	dataLines.append(DigitalInputDevice(dataLineId, True))
	
# Set all address lines for output
for addressLineId in addressLineIds:
	addressLines.append(DigitalOutputDevice(addressLineId, True, True))

# Just record what time the key was pressed
def buttonPressed():
    print('Button pressed')
	
modeButton.when_pressed = buttonPressed

# Announce
print("Running")

try:

	# Loop forever
	while True:
		
		# Individually set each address line low
		for addressLine in range(8):
			
			# Set low
			addressLines[addressLine].off()
			
			# Scan data lines
			for dataLine in range(5):
				
				# Get state and details for this button
				isPressed = dataLines[dataLine].value == 1

				if(keyboardMode == 0):
					keyPressed = keys[addressLine][dataLine]
				else:
					keyPressed = funcKeys[addressLine][dataLine]
				
				# If pressed for the first time
				if(isPressed and keyTrack[addressLine][dataLine] == False):

					# Press the key and make a note
					print('Pressed ' + keyPressed)
					keyTrack[addressLine][dataLine] = True

				# If not pressed now but was pressed on last check
				elif(not isPressed and keyTrack[addressLine][dataLine] == True):
					
					# Release the key and make a note
					print('Released ' + keyPressed)
					keyTrack[addressLine][dataLine] = False

			# Set high
			addressLines[addressLine].on()
		

except KeyboardInterrupt:
	sys.exit(0)
