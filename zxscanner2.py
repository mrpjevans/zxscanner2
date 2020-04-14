#
# ZX Raspberry Keyboard Scanner v5
# @mrpjevans mrpjevans.com 2019
# MIT License (https://opensource.org/licenses/MIT) see LICENSE
#

import time, sys, uinput, os
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

# Well this is annoying
device = uinput.Device([
        uinput.KEY_A, uinput.KEY_B, uinput.KEY_C, uinput.KEY_D, uinput.KEY_E, uinput.KEY_F, uinput.KEY_G, uinput.KEY_H,
        uinput.KEY_I, uinput.KEY_J, uinput.KEY_K, uinput.KEY_L, uinput.KEY_M, uinput.KEY_N, uinput.KEY_O, uinput.KEY_P,
		uinput.KEY_Q, uinput.KEY_R, uinput.KEY_S, uinput.KEY_T, uinput.KEY_U, uinput.KEY_V, uinput.KEY_W, uinput.KEY_X,
        uinput.KEY_Y, uinput.KEY_Z, uinput.KEY_0, uinput.KEY_1, uinput.KEY_2, uinput.KEY_3, uinput.KEY_4, uinput.KEY_5,
        uinput.KEY_6, uinput.KEY_7, uinput.KEY_8, uinput.KEY_9,
        uinput.KEY_LEFTSHIFT, uinput.KEY_ENTER, uinput.KEY_SPACE, uinput.KEY_LEFTCTRL,
        uinput.KEY_F1, uinput.KEY_F2, uinput.KEY_F3, uinput.KEY_F4, uinput.KEY_F5,
        uinput.KEY_UP, uinput.KEY_DOWN, uinput.KEY_LEFT, uinput.KEY_RIGHT,
        uinput.KEY_ESC
        ])

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
	global buttonTime
	buttonTime = int(time.time())

# Button actions take place on release
def buttonReleased():
	global buttonTime, keyboardMode

	timePressed = int(time.time()) - buttonTime

	# If less than 2 secs, switch keyboard mode
	if timePressed <= 3:

		# Switch modes
		if keyboardMode == 0:
			print("Switching to Function Keys")
			keyboardMode = 1;
			os.system('mpg123 -q ding2.mp3 &')
		else:
			print("Switching to Spectrum Keys")
			keyboardMode = 0;
			os.system('mpg123 -q ding1.mp3 &')


	elif timePressed <= 6:

		print('Killing FUSE')
		os.system('sudo killall fuse-sdl')

	else:

		print('Shutting down')
		os.system('sudo shutdown -h now')

modeButton.when_pressed = buttonPressed
modeButton.when_released = buttonReleased

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
				keyCode = getattr(uinput, 'KEY_' + keyPressed)

				# If pressed for the first time
				if(isPressed and keyTrack[addressLine][dataLine] == False):

					# Press the key and make a note
					print('Pressing ' + keyPressed)
					device.emit(keyCode, 1)
					keyTrack[addressLine][dataLine] = True

				# If not pressed now but was pressed on last check
				elif(not isPressed and keyTrack[addressLine][dataLine] == True):

					# Release the key and make a note
					print('Releasing ' + keyPressed)
					device.emit(keyCode, 0)
					keyTrack[addressLine][dataLine] = False

			# Set high
			addressLines[addressLine].on()

		# Allow the CPU to breathe
		time.sleep(0.01)


except KeyboardInterrupt:
	sys.exit(0)
