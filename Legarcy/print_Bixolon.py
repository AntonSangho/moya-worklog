"""
Requirement
gcc
cups-devel(libcups-2dev)
python3-devel (python3 dev)

Printe on demand with rasberrypi (https://www.hackster.io/glowascii/print-on-demand-with-raspi-d74619)
GPIO pin:

"""
# !/bin/python

import RPi.GPIO as GPIO
import time
import os
#import cups
import random 
from escpos import *
from PIL import Image

#conn = cups.Connection()
#printers = conn.getPrinters()
p = printer.Usb(0x1504, 0x006e, in_ep=0x81, out_ep=0x02)

file1 = "/home/pi/moya-worklog/image/w1.png"
#file2 는 제거
#file2 = "/home/pi/moya-worklog/image/w2.png"
file3 = "/home/pi/moya-worklog/image/w3.png"
file4 = "/home/pi/moya-worklog/image/w4.png"
file5 = "/home/pi/moya-worklog/image/w5.png"
filelist = [file1, file3, file4, file5]

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setwarnings(False)
GPIO.setup(20, GPIO.OUT)
print("LED on")
GPIO.output(20, GPIO.HIGH)
time.sleep(1)

#os.system('lp /usr/share/cups/data/testprint')
os.system('cancel -a')

def Print(channel):
	im = Image.open(random.choice(filelist))	
	out = im.resize((480, 1000))
	p.image(out)
	p.cut()

GPIO.add_event_detect(21, GPIO.RISING, callback=Print, bouncetime=2000)

while 1:
    time.sleep(1)
