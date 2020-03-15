# Pan and Tilt Module
# ===================
# Be sure to position the motors to their "default" position
# before running this module or risk your motors rotating past
# where they're not suppose to rotate to, thus breaking your
# mechanism.

import RPi.GPIO as GPIO
import time
import math

# set pin numbers to the board's
GPIO.setmode(GPIO.BOARD)

class Stepper:
    # Class variables
    microStep = ['Full Step', 'Half Step', 'Quarter step', 'Eighth Step', 'Sixteenth Step']
    stepperPos = 0.0 # Initial position, (which is the position the motor was turned on)
    stepperSteps = 1.8 # Default at full step @ 1.8 deg
    stepperPosMin = -45.0 # -45 deg max, can be changed
    stepperPosMax = 45.0 # 45 deg max, can be changed
    pulseWidth = 4e-3 # Speed of pulse in seconds, lower number = faster but may skip

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

    def rotateCCW(self):
        GPIO.output(self.dirPin, GPIO.LOW)
        if self.stepperPos <= self.stepperPosMin:
            print("Max forward angle")
        else:
            self.givePulse()
            self.stepperPos -= self.stepperSteps

    def rotateCW(self):
        GPIO.output(self.dirPin, GPIO.HIGH)
        if self.stepperPos >= self.stepperPosMax:
            print("Max backwards angle")
        else:
            self.givePulse()
            self.stepperPos += self.stepperSteps

# Default pins for the pan and tilt stepper motor driver
tilt = Stepper(19 , 21)
pan = Stepper(22, 24)

# To test out the Pan and Tilt stepper motors, uncomment
"""
while (1):

    print("Tilting forward")
    for i in range(70):
        tilt.rotateCCW()
        print(tilt.stepperPos)
    time.sleep(0.5)

    print("Tilting backwards")
    # Go backwards
    for i in range(70):
        tilt.rotateCW()
        print(tilt.stepperPos)
    time.sleep(0.5)

    while (math.floor(tilt.stepperPos)):
        tilt.rotateCCW()
        print(tilt.stepperPos)
    time.sleep(0.5)

    print("Panning left")
    # Go backwards
    for i in range(70):
        pan.rotateCCW()
        print(pan.stepperPos)
    time.sleep(0.5)

    print("Panning right")
    # Go backwards
    for i in range(70):
        pan.rotateCW()
        print(pan.stepperPos)
    time.sleep(0.5)

    while (math.floor(pan.stepperPos)):
        pan.rotateCCW()
        print(pan.stepperPos)
    time.sleep(0.5)

GPIO.cleanup()
"""