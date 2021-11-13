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

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setwarnings(False)
GPIO.setup(20, GPIO.OUT)
print("LED on")
GPIO.output(20, GPIO.HIGH)
time.sleep(1)
print(printers)

#os.system('lp /usr/share/cups/data/testprint')

def Printtest(channel):
    print('Printing...')
    conn.printFile('BIXOLON_SRP-330II', random.choice(filelist), "working diary", {})

def cancel_all_jobs(self, printer_id):
    jobs = self.get_jobs()
    try:
        conn = self.get_connection()
        for job_id in jobs:
            job = jobs[job_id]
            if jobs[job_id]['printer-uri'].endswith(printer_id):
                conn.cancelJob(int(job_id))
        self.bad_password = False
    except (cups.IPPError) as e:
        abort(403)


#GPIO.add_event_detect(21, GPIO.RISING, callback=Printtest, bouncetime=2000)
GPIO.add_event_detect(21, GPIO.RISING, callback=cancel_all_jobs, bouncetime=2000)

while 1:
    time.sleep(1)
