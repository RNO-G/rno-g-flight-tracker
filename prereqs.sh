#! /bin/sh 

#This runs at least on a raspberry pi 4 with Debian 10.7

echo "Installing udev rules" 
sudo wget -O  /etc/udev/rules.d/90-rtl-sdr.rules "https://raw.githubusercontent.com/osmocom/rtl-sdr/master/rtl-sdr.rules"

echo "Installing dump1090-mutability, sqlite3" 
sudo apt install dump1090-mutability sqlite3

echo "Adding dump1090 to plugdev" 
usermod -a -G plugdev dump1090 

echo "Reboot or reseat USB/restart dump1090 for everything to take effect, probably?" 
