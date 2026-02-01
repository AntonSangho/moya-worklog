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

# Bixolon printer
p = printer.Usb(0x1504, 0x006e, in_ep=0x81, out_ep=0x02)

file1 = "/home/pi/moya-worklog/image/w1_2022.png"
file2 = "/home/pi/moya-worklog/image/w2_2022.png"
file3 = "/home/pi/moya-worklog/image/w3_2022.png"
file4 = "/home/pi/moya-worklog/image/w4_2022.png"
file5 = "/home/pi/moya-worklog/image/w5_2022.png"
filelist = [file1, file2, file3, file4, file5]

# GPIO 핀 설정
BUTTON_PINS = [2, 21]  # 두 GPIO 핀 모두 버튼으로 허용
LED_PIN = 20

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 버튼 핀 설정 (GPIO 2, 21 모두 지원)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# LED 핀 설정
GPIO.setup(LED_PIN, GPIO.OUT)
print("LED on")
GPIO.output(LED_PIN, GPIO.HIGH)
time.sleep(1)
count = 0

def print_sam4s(channel):
    im = Image.open(random.choice(filelist))
    out = im.resize((480, 1000))
    p.image(out)
    p.cut()

def print_test(channel):
    global count 
    count +=1
    print("print_test" + str(count))
    im = Image.open(random.choice(filelist))
    p.text(str(count) + "\n")
    p.cut()

# 두 버튼 핀 모두 이벤트 감지
for pin in BUTTON_PINS:
    GPIO.add_event_detect(pin, GPIO.RISING, callback=print_sam4s, bouncetime=2000)

print(f"버튼 GPIO {BUTTON_PINS} 대기 중...")

try:
    while True:
        pass
except KeyboardInterrupt:
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()
