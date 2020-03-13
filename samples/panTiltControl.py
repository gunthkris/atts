# Testing Pan and Tilt

import RPi.GPIO as GPIO
import time

# set pin numbers to the board's
GPIO.setmode(GPIO.BOARD)

class Stepper:

    microStep = 'FS'
    stepperPos = 0.0
    stepperSteps = 1.8 # Default at full step
    stepperPosMin = -45.0 # 1.8 deg with full step (45 deg max)
    stepperPosMax = 45.0 # same
    pulseWidth = 100e-6 # Speed of pulse in seconds

    # Define pins for step and direction
    def __init__(self, stepPin, dirPin):
        self.stepPin = stepPin
        self.dirPin = dirPin
        GPIO.setup(self.stepPin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.dirPin, GPIO.OUT, initial=GPIO.LOW)

    def givePulse(self):
        GPIO.output(self.stepPin, GPIO.HIGH)
        time.sleep(self.pulseWidth)
        GPIO.output(self.stepPin, GPIO.LOW)
        time.sleep(self.pulseWidth)

    def tiltFwd(self):
        GPIO.output(self.dirPin, GPIO.LOW)
        if self.stepperPos <= self.stepperPosMin:
            print("Max forward angle")
        else:
            self.givePulse()
            self.stepperPos -= self.stepperSteps

    def tiltBwd(self):
        GPIO.output(self.dirPin, GPIO.HIGH)
        if self.stepperPos >= self.stepperPosMax:
            print("Max backwards angle")
        else:
            self.givePulse()
            self.stepperPos += self.stepperSteps

tilt = Stepper(19 , 21)

while (1):
    print("Going forward")
    for i in range(200):
        tilt.tiltFwd()
        print(tilt.stepperPos)

    time.sleep(1)
    print("Going backwards")
    # Go backwards

    for i in range(200):
        tilt.tiltBwd()
        print(tilt.stepperPos)

    time.sleep(1)

GPIO.cleanup()
