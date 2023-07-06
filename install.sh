#!/bin/bash

# Update package lists
sudo apt-get update -y

# Upgrade installed packages 
sudo apt-get upgrade -y

# Install python3-dev
sudo apt-get install -y python3-dev

# Install python3-pip
sudo apt-get install -y python3-pip

# Install cups
sudo apt-get install -y cups

# Install escpos
sudo apt-get install -y escpos

# Install libcups2-dev
sudo apt-get install -y libcups2-dev

# Add content to boot.ini
sudo sed -i '/# Load kernel, dtb and initrd/i ### in case of GPIOX.3 (Pin 11) of 2x20 pins connector\nsetenv gpiopower "479"\nsetenv bootargs ${bootargs} gpiopower=${gpiopower}' /media/boot/boot.ini

# Clone RPi.GPIO-Odroid repository
git clone https://github.com/awesometic/RPi.GPIO-Odroid

# Build and install RPi.GPIO-Odroid
cd RPi.GPIO-Odroid
python setup.py build
sudo python setup.py install

# Clone moya-worklog repository
git clone --recurse-submodules https://github.com/AntonSangho/moya-worklog.git

# Install requirements for moya-worklog
cd moya-worklog/odroid
pip install -r requirements.txt

# Add command to /etc/rc.local
sudo sed -i '/^exit 0/i sudo python3 /root/moya-worklog/odroid/print_odroid.py &' /etc/rc.local
