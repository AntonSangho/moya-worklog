"""
Requirement
Odroid C-4
Bixolon

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
#p = printer.Usb(0x1c8a, 0x3a0e, in_ep=0x81, out_ep=0x02)

#Bixolon Printer
#p = printer.Usb(0x1504, 0x006e, in_ep=0x81, out_ep=0x02)
"""
file1 = "/home/pi/moya-worklog/image/w1_2022.png"
file2 = "/home/pi/moya-worklog/image/w2_2022.png"
file3 = "/home/pi/moya-worklog/image/w3_2022.png"
file4 = "/home/pi/moya-worklog/image/w4_2022.png"
file5 = "/home/pi/moya-worklog/image/w5_2022.png"
filelist = [file1, file2, file3, file4, file5]
"""
file1 = "/root/moya-worklog/image/w1_2022.png"
file2 = "/root/moya-worklog/image/w2_2022.png"
file3 = "/root/moya-worklog/image/w3_2022.png"
file4 = "/root/moya-worklog/image/w4_2022.png"
file5 = "/root/moya-worklog/image/w5_2022.png"
filelist = [file1, file2, file3, file4, file5]

#GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#GPIO.setwarnings(False)
#GPIO.setup(20, GPIO.OUT)
#GPIO.setup(13, GPIO.OUT)
#print("LED on")
#GPIO.output(20, GPIO.HIGH)
#GPIO.output(13, GPIO.HIGH)
#time.sleep(1)

#os.system('lp /usr/share/cups/data/testprint')
#os.system('cancel -a')

IRQ_GPIO_PIN = 25
LED_GPIO_PIN = 21
#IRQ_EDGE = GPIO.FALLING
IRQ_EDGE = GPIO.RISING
count = 0

def handler(channel):
    global count

    count += 1

def print_status():
    global count
    #GPIO.digitalWrite(0, 1)
    print(count)
    count = 0

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(IRQ_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(IRQ_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    #GPIO.setup(LED_GPIO_PIN, GPIO.OUT)
    GPIO.add_event_detect(IRQ_GPIO_PIN, IRQ_EDGE, callback=handler)

    print('Press Ctrl-C to exit')
    try:
        while True:
            time.sleep(1)
            print_status()
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit(0)

def Printtest(channel):
    print('Printing...')
    conn.printFile('BIXOLON_SRP-330II', random.choice(filelist), "working diary", {})

def Print_sam4s(channel):
	im = Image.open(random.choice(filelist))
	out = im.resize((480, 1000))
	#p.image(out)
	#p.cut()


#Print_sam4s(0)
#GPIO.add_event_detect(21, GPIO.RISING, callback=Print_sam4s, bouncetime=2000)

#while 1:
#    time.sleep(1)



