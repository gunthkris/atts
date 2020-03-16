# Pan and Tilt Module
# ===================
# Be sure to position the motors to their "default" position
# before running this module or risk your motors rotating past
# where they're not suppose to rotate to, thus breaking your
# mechanism.
# +------+------+------+----------------------+
# | MS1  | MS2  | MS3  | Microstep Resolution |
# +------+------+------+----------------------+
# | Low  | Low  | Low  | Full step            |
# | High | Low  | Low  | Half step            |
# | Low  | High | Low  | Quarter step         |
# | High | High | Low  | Eighth step          |
# | High | High | High | Sixteenth step       |
# +------+------+------+----------------------+

import RPi.GPIO as GPIO
import time
import math

# set pin numbers to the board's
GPIO.setmode(GPIO.BOARD)

class Stepper:
    # Class variables
    microStep = "Full Step" # Default
    stepperPos = 0.0 # Initial position, (which is the position the motor was turned on)
    stepperSteps = 1.8 # Default at full step @ 1.8 deg (0.9, 0.45, 0.225, 0.1125)
    stepperPosMin = -45.0 # -45 deg max, can be changed
    stepperPosMax = 45.0 # 45 deg max, can be changed
    pulseWidth = 5e-6 # Speed of pulse in seconds, lower number = faster but may skip

    # Define pins for step and direction
    def __init__(self, name, stepPin, dirPin, ms1Pin, ms2Pin, ms3Pin):
        self.name = name
        self.stepPin = stepPin
        self.dirPin = dirPin
        self.ms1Pin = ms1Pin
        self.ms2Pin = ms2Pin
        self.ms3Pin = ms3Pin
        GPIO.setup(self.stepPin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.dirPin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.ms1Pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.ms2Pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.ms3Pin, GPIO.OUT, initial=GPIO.LOW)

    def setMicroStep(self, microStep):
        self.microStep = microStep
        if self.microStep == "Full Step":
            self.stepperSteps = 1.8
            GPIO.output(self.ms1Pin, GPIO.LOW)
            GPIO.output(self.ms2Pin, GPIO.LOW)
            GPIO.output(self.ms3Pin, GPIO.LOW)
        elif self.microStep == "Half Step":
            self.stepperSteps = 0.9
            GPIO.output(self.ms1Pin, GPIO.HIGH)
            GPIO.output(self.ms2Pin, GPIO.LOW)
            GPIO.output(self.ms3Pin, GPIO.LOW)
        elif self.microStep == "Quarter Step":
            self.stepperSteps = 0.45
            GPIO.output(self.ms1Pin, GPIO.LOW)
            GPIO.output(self.ms2Pin, GPIO.HIGH)
            GPIO.output(self.ms3Pin, GPIO.LOW)
        elif self.microStep == "Eighth Step":
            self.stepperSteps = 0.225
            GPIO.output(self.ms1Pin, GPIO.HIGH)
            GPIO.output(self.ms2Pin, GPIO.HIGH)
            GPIO.output(self.ms3Pin, GPIO.LOW)
        elif self.microStep == "Sixteenth Step":
            self.stepperSteps = 0.1125
            GPIO.output(self.ms1Pin, GPIO.HIGH)
            GPIO.output(self.ms2Pin, GPIO.HIGH)
            GPIO.output(self.ms3Pin, GPIO.HIGH)
        else:
            self.microStep = "Full Step"
            self.stepperSteps = 1.8
            GPIO.output(self.ms1Pin, GPIO.LOW)
            GPIO.output(self.ms2Pin, GPIO.LOW)
            GPIO.output(self.ms3Pin, GPIO.LOW)
        time.sleep(250e-9) # Wait time to setup steps

    def givePulse(self):
        GPIO.output(self.stepPin, GPIO.HIGH)
        time.sleep(self.pulseWidth)
        GPIO.output(self.stepPin, GPIO.LOW)
        time.sleep(self.pulseWidth)
        print("{} Pos: {} Step: {}".format(self.name, self.stepperPos, self.stepperSteps))

    def rotateCCW(self):
        GPIO.output(self.dirPin, GPIO.LOW)
        time.sleep(250e-9) # Wait time to setup steps
        if self.stepperPos <= self.stepperPosMin:
            print("Minimum angle reached")
        else:
            self.givePulse()
            self.stepperPos -= self.stepperSteps

    def rotateCW(self):
        GPIO.output(self.dirPin, GPIO.HIGH)
        time.sleep(250e-9) # Wait time to setup steps
        if self.stepperPos >= self.stepperPosMax:
            print("Maximum angle reached")
        else:
            self.givePulse()
            self.stepperPos += self.stepperSteps

# Default pins for the pan and tilt stepper motor driver
tilt = Stepper("Tilt", 19 , 21, 12, 16, 18)
pan = Stepper("Pan", 22, 24, 36, 38, 40)

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