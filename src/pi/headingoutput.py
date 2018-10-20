import RPi.GPIO as GPIO
import time
import requests
import threading
import buttoninput2 as bttns

# Shift Register pinouts
SREG_DS = 16
SREG_ST_CP = 18
SREG_SH_CP = 22

# Rotary pinouts
ROTARY_CLK = 29
ROTARY_DT = 31

#      0     1     2     3     4     5     6     7     8     9
NUM = (0xEE, 0x28, 0xB6, 0xBC, 0x78, 0xDC, 0xDE, 0xA8, 0xFE, 0xFC)

# Digit control pinouts
DIGITS = (11, 13, 15, 19)

LEFT = 1
RIGHT = -1

HEADING_URL = "http://192.168.1.104:8558/autopilot/heading"
AP_URL = "http://192.168.1.104:8558/autopilot/enabled"
HEADING_HOLD_URL = "http://192.168.1.104:8558/autopilot/headingHold"

USE_HOOK = True


rotaryMoving = False
rotaryDirection = 0
heading = 270
staleHeading = True

def setupSevenSegment():
	GPIO.setup(SREG_DS, GPIO.OUT)
	GPIO.setup(SREG_ST_CP, GPIO.OUT)
	GPIO.setup(SREG_SH_CP, GPIO.OUT)
	
	for digit in DIGITS:
		GPIO.setup(digit, GPIO.OUT)
		
def setupRotary():
	GPIO.setup(ROTARY_CLK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(ROTARY_DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def setup():
	setupSevenSegment()
	setupRotary()
		
def cleanup():
	GPIO.cleanup()

def disableDigits():
	for index in range(len(DIGITS)):
		GPIO.output(DIGITS[index], GPIO.HIGH)

def enableDigit(digitIndex):
	# digit 0, 1, 2, 3
	for index in range(len(DIGITS)):
		output = GPIO.HIGH
		if index == digitIndex:
			output = GPIO.LOW
		
		GPIO.output(DIGITS[index], output)

def outputData(bits):
	# set latch low
	GPIO.output(SREG_ST_CP, GPIO.LOW)
	
	# for each bit of the value	
	for i in range(0, 8):
	
		# set clock low
		GPIO.output(SREG_SH_CP, GPIO.LOW)
		
		# write bit
		
		output = GPIO.HIGH
		if 0x01 & (bits >> i) == 0x01:
			output = GPIO.LOW
		
		GPIO.output(SREG_DS, output)
		
		# set clock high
		GPIO.output(SREG_SH_CP, GPIO.HIGH)
		
	# set latch high
	GPIO.output(SREG_ST_CP, GPIO.HIGH)

def outputValue(value):
	# select 3
	
	CLEAR = 0x00
	
	outputData(CLEAR)
	enableDigit(3)	
	ones = value % 10
	outputData(NUM[ones])
	time.sleep(0.001)
	
	outputData(CLEAR)
	enableDigit(2)
	tens = value % 100 // 10
	outputData(NUM[tens])
	time.sleep(0.001)
	
	outputData(CLEAR)
	enableDigit(1)
	hundreds = value % 1000 // 100
	outputData(NUM[hundreds])
	time.sleep(0.001)
	
	outputData(CLEAR)
	#enableDigit(0)
	#thousands = value % 10000 // 1000
	#outputData(NUM[thousands])
	#time.sleep(0.001)
	
	# get tens value

def readRotary():
	global heading
	global rotaryDirection
	global rotaryMoving
	global staleHeading
	
	clkVal = GPIO.input(ROTARY_CLK)
	dtVal = GPIO.input(ROTARY_DT)
	
	if (not rotaryMoving):
		if (clkVal == 0) or (dtVal == 0):
			rotaryMoving = True
			if dtVal == 0 and clkVal == 1:
				rotaryDirection = LEFT
			elif dtVal == 1 and clkVal == 0:
				rotaryDirection = RIGHT
	else:
		if (clkVal == 1) and (dtVal == 1):
			heading += rotaryDirection
			staleHeading = True
			rotaryMoving = False
			
	if heading < 0:
		heading += 360
		staleHeading = True
	if heading > 359:
		heading -= 360
		staleHeading = True

t = 0

def timer():
	global t
	global timer
	global heading
	global staleHeading
		
	if not USE_HOOK:
		heading = 133
		return
		
	# Heading
		
	if staleHeading:
		requests.post(HEADING_URL,str(heading))
		staleHeading = False

	headingStr = requests.get(HEADING_URL).text
	heading = int(headingStr)
	
	# Autopilot Enable
	
	apStr = requests.get(AP_URL).text
	
	apValue = 0
	if apStr == "True":
		apValue = 1
		
	if buttons._btnInputs[bttns.BTN_AP] > 0:
		if apStr == "True":
			apStr = "False"
		else:
			apStr = "True"
		requests.post(AP_URL, apStr)
		
	buttons._ledValues[bttns.BTN_AP] = apValue
	
	# Heading Hold
	
	hhStr = requests.get(HEADING_HOLD_URL).text
	
	print(hhStr)
	
	hhValue = 0
	if hhStr == "True":
		hhValue = 1
		
	if buttons._btnInputs[bttns.BTN_HDG] > 0:
		if hhStr == "True":
			hhStr = "False"
		else:
			hhStr = "True"
		requests.post(HEADING_HOLD_URL, hhStr)
		
	buttons._ledValues[bttns.BTN_HDG] = hhValue
	
	# End
	
	buttons.resetInputs()
	
	t = threading.Timer(1.0, timer)
	t.start()

buttons = bttns.ButtonCluster()

def loop():
	global heading
	
	timer()
	
	while True:
		outputValue(heading)
		readRotary()
		buttons.readButtons()
		
		buttons.writeLeds()
		

def main(args):
	GPIO.setmode(GPIO.BOARD)
	setup()
	buttons.setup()
	try:
		loop()
	except KeyboardInterrupt:
		cleanup()
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
