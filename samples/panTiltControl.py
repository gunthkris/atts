# Testing Pan and Tilt

import RPi.GPIO as GPIO
import time

# set pin numbers to the board's
GPIO.setmode(GPIO.BOARD)
steps = 0.0005 # Speed of pulse in seconds

class Stepper:

    microStep = 'FS'
    stepperPos = 0
    stepperSteps = 1.8 # Default at full step
    stepperPosMin = -45.0 # 1.8 deg with full step (45 deg max)
    stepperPosMax = 45.0 # same
    steps = 0.0005

    # Define pins for step and direction
    def __init__(self, stepPin, dirPin):
        self.stepPin = stepPin
        self.dirPin = dirPin
        GPIO.setup(self.stepPin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.dirPin, GPIO.OUT, initial=GPIO.LOW)

    def outOBounds:
        if stepperPos <= stepperPosMin or stepperPos >= stepperPosMax
            return true

    def givePulse:
        GPIO.output(stepPin, GPIO.HIGH)
        time.sleep(steps)
        GPIO.output(stepPin, GPIO.LOW)
        time.sleep(steps)

    def tiltFwd:
        GPIO.output(dirPin, GPIO.LOW)
        if outOfBounds():
            break
            print("Max forward angle")
        else:
            givePulse()
            stepperPos -= stepperSteps

    def tiltBwd:
        GPIO.output(dirPin, GPIO.HIGH)
        if outOfBounds():
            break
            print("Max backwards angle")
        else:
            givePulse()
            stepperPos += stepperSteps

tiltStepper = Stepper(19, 21)

while (1):
    print("Going forward")
    for i in range(200):
        tiltStepper.tiltFwd()
        print(tiltStepper.stepperPos)

    time.sleep(1)
    print("Going backwards")
    # Go backwards

    for i in range(200):
        tiltStepper.tiltBwd()
        print(tiltStepper.stepperPos)

    time.sleep(1)

GPIO.cleanup()
