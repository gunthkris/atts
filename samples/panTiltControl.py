# Testing Pan and Tilt

import RPi.GPIO as GPIO
import time

stepPin = 33
dirPin = 35

# set pin numbers to the board's
GPIO.setmode(GPIO.BOARD)

GPIO.setup(stepPin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(dirPin, GPIO.OUT, initial=GPIO.HIGH)

for i in range (200):
    GPIO.output(stepPin, GPIO.HIGH)
    time.sleep(0.0005)
    GPIO.output(stepPin, GPIO.LOW)
    time.sleep(0.0005)

# Go backwards
GPIO.output(dirPin, GPIO.LOW)

for i in range (200):
    GPIO.output(stepPin, GPIO.HIGH)
    time.sleep(0.0005)
    GPIO.output(stepPin, GPIO.LOW)
    time.sleep(0.0005)

GPIO.cleanup()