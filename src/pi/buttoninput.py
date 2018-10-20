import RPi.GPIO as GPIO
import time
import threading

BTN_AP = 4   # 0
BTN_HDG = 5  # 1
BTN_NAV = 6  # 2
BTN_APR = 7  # 3
BTN_REV = 0  # 4
BTN_ALT = 1  # 5

class ButtonCluster(object):
    BTN_LOAD = 36
    BTN_CLK = 38
    BTN_DT = 40
    DIGIT_DT = 33
    DIGIT_CLK = 37 # SH_CP
    DIGIT_LATCH = 35 # ST_CP
    LEDBTN_INDEX = [2, 3, 4, 5, 6, 7, 0, 1]

    def __init__(self):
        self._ledValues = [0, 0, 99, 99, 0, 0, 0, 0]
        
        self._btnInputs = [0, 0, 0, 0, 0, 0, 0, 0]

    def resetInputs(self):
        self._btnInputs = [0, 0, 0, 0, 0, 0, 0, 0]

    def setup(self):
        GPIO.setup(self.BTN_LOAD, GPIO.OUT)
        GPIO.setup(self.BTN_CLK, GPIO.OUT)
        GPIO.setup(self.BTN_DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.DIGIT_DT, GPIO.OUT)
        GPIO.setup(self.DIGIT_CLK, GPIO.OUT)
        GPIO.setup(self.DIGIT_LATCH, GPIO.OUT)

    def cleanup(self):
        GPIO.cleanup()
	
    def writeLeds(self):
        GPIO.output(self.DIGIT_LATCH, GPIO.LOW)
        for index in range(len(self.LEDBTN_INDEX)):
            GPIO.output(self.DIGIT_CLK, GPIO.LOW)
            value = self._ledValues[self.LEDBTN_INDEX[index]]
            if value > 0:
                GPIO.output(self.DIGIT_DT, GPIO.HIGH)
            else:
                GPIO.output(self.DIGIT_DT, GPIO.LOW)
            GPIO.output(self.DIGIT_CLK, GPIO.HIGH)
        GPIO.output(self.DIGIT_LATCH, GPIO.HIGH)
        
    def readButtons(self):
        GPIO.output(self.BTN_CLK, GPIO.HIGH)
        
        GPIO.output(self.BTN_LOAD, GPIO.HIGH)
        GPIO.output(self.BTN_LOAD, GPIO.LOW)
        GPIO.output(self.BTN_LOAD, GPIO.HIGH)
        
        for index in range(len(self._btnInputs)):
            GPIO.output(self.BTN_CLK, GPIO.HIGH)
            
            inval = GPIO.input(self.BTN_DT)
            
            if inval > 0:
                self._btnInputs[index] = inval
                
            GPIO.output(self.BTN_CLK, GPIO.LOW)

def main(args):
    buttons = ButtonCluster()
    buttons.setup()
    try:
        buttons = ButtonCluster()

        while True:
            buttons.readButtons()
            buttons.writeLeds()
    except KeyboardInterrupt:
        buttons.cleanup()
        return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
