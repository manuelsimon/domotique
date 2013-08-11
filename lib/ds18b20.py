#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This little example code checks and parses the temperature from
# a DS18B20 connected to GPIO 4 on the Raspberry Pi running Occidentalis
# By Monirul Pathan

# Connect a DS18B20 with VCC to 3V, ground to ground and Data
# to GPIO #4. Then connect a 4.7K resistor from Data to VCC.

# Rus on Occidentalis: http://learn.adafruit.com/adafruit-raspberry-pi-educational-linux-distro/occidentalis-v0-dot-1
# Thanks Adafruit for the awesome RPi distro =)

import glob
import time
import os
import sys
import MySQLdb
import ntpath

def init():
	#initialize the device
	os.system("sudo modprobe w1-gpio")
	os.system("sudo modprobe w1-therm")

def insertTemperature(datetimeReleve, sonde, temperature):
	conn = MySQLdb.connect(host= "localhost",
					  db="test")
	x = conn.cursor()

	try:
	   x.execute("""INSERT INTO RELEVE_TEMPERATURE VALUES (%s,%s,%s)""", (time.strftime('%Y-%m-%d %H:%M:%S'), sonde, temperature))
	   conn.commit()
	except:
	   conn.rollback()

	conn.close()

def getTemperature(deviceName):
	device="/sys/bus/w1/devices/" + deviceName + "/w1_slave"
	#open up the file
	f = open (device, 'r')
	sensor = f.readlines()
	f.close()

	#parse results from the file
	crc=sensor[0].split()[-1]
	temp=float(sensor[1].split()[-1].strip('t='))
	temp_C=(temp/1000.000)

	temperature=None
	if 'YES' in crc:
		temperature=temp_C
		
	return temperature

def getDevicesName():
	devicesName=[]
	
	#find the device
	devicesDir = glob.glob("/sys/bus/w1/devices/28-*")
	for deviceDir in devicesDir:
		deviceName=ntpath.basename(deviceDir);
		devicesName.append(deviceName);
		
	return devicesName;
	