"""
Requirement
gcc
cups-devel(libcups-2dev)
python3-devel (python3 dev)

Printe on demand with rasberrypi (https://www.hackster.io/glowascii/print-on-demand-with-raspi-d74619)
GPIO pin: 20, 21

"""
# !/bin/python

import RPi.GPIO as GPIO
import time
import os
import cups
import random

conn = cups.Connection()
printers = conn.getPrinters()
button_pin = 21
led_pin = 20

file1 = "/home/pi/moya-worklog/image/w1.png"
file2 = "/home/pi/moya-worklog/image/w2.png"
file3 = "/home/pi/moya-worklog/image/w3.png"
file4 = "/home/pi/moya-worklog/image/w4.png"
file5 = "/home/pi/moya-worklog/image/w5.png"
filelist = [file1, file2, file3, file4, file5]

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set button pin in software pull down.

GPIO.setwarnings(False)
GPIO.setup(led_pin, GPIO.OUT, initial=1)
print("LED on")
GPIO.output(led_pin, True) # LED on in the starts.

#os.system('lp /usr/share/cups/data/testprint')

def PrintJob(channel):
    print('Printing...')
    conn.printFile('BIXOLON_SRP-330II', random.choice(filelist), "working diary", {})

while True:
	if GPIO.input(button_pin) == True:
		print('button pressed')
		PrintJob(button_pin)
		GPIO.output(led_pin, False) # LED off when the button is pressed.
		time.sleep(1)
	else:
		GPIO.output(led_pin, True)
