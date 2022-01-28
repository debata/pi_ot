import RPi.GPIO as GPIO #import the GPIO library
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)


while True:
    if GPIO.input(2):
       print("Door is open")
       time.sleep(2)
    if GPIO.input(2) == False:
       print("Door is closed")
       time.sleep(2)
