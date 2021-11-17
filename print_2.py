import RPi.GPIO as GPIO  
from time import sleep     # this lets us have a time delay (see line 15)  
import cups
import random

conn = cups.Connection()
printers = conn.getPrinters()
file1 = "/home/pi/moya-worklog/image/w1.png"
file2 = "/home/pi/moya-worklog/image/w2.png"
file3 = "/home/pi/moya-worklog/image/w3.png"
file4 = "/home/pi/moya-worklog/image/w4.png"
file5 = "/home/pi/moya-worklog/image/w5.png"
filelist = [file1, file2, file3, file4, file5]

GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)    # set GPIO25 as input (button)  
GPIO.setup(20, GPIO.OUT)   # set GPIO20 as an output (LED)  
  
def Printtest(channel):
    print('Printing...')
    conn.printFile('BIXOLON_SRP-330II', random.choice(filelist), "working diary", {})

#GPIO.add_event_detect(21, GPIO.RISING, callback=Printtest, bouncetime=2000)

try:  
    while True:            # this will carry on until you hit CTRL+C  
        if GPIO.input(21): # if port 21 == 1  
            print "Port 21 is 1/HIGH/True - LED ON"  
            Printtest()
            GPIO.output(20, 1)         # set port/pin value to 1/HIGH/True  
        else:  
            print "Port 21 is 0/LOW/False - LED OFF"  
            GPIO.output(20, 0)         # set port/pin value to 0/LOW/False  
        sleep(0.1)         # wait 0.1 seconds  
  
finally:                   # this block will run no matter how the try block exits  
    GPIO.cleanup()         # clean up after yourself  