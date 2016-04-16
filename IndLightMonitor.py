#!/usr/bin/python

import sys
import time
#Adafruit_I2C from https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_I2C/Adafruit_I2C.py
#from Adafruit_I2C import Adafruit_I2C
import ConfigParser
import io
from TSL2561 import TSL2561
from time import sleep


def readConfig(filename):
	try:
		with open(filename) as cfgfile:
			cfg = cfgfile.read()
			config = ConfigParser.RawConfigParser(allow_no_value=True)
			config.readfp(io.BytesIO(cfg))
		return config
	except IOError:
		print "Can not open configuration file: " + filename

def variance(numbers):
	average = sum(numbers)/len(numbers) * 1.0
	numerator = 0
	for i in numbers:
		numerator = numerator + ((i - average) ** 2)
		
	return numerator / len(numbers)


if __name__ == "__main__":
	config = readConfig("indlightmonitor.config")
	#print(config)
	sensor_name= config.get('sensor','sensor_name')
	i2c_address= int(config.get('sensor','i2c_address'),16)
	if config.get('sensor','gain').lower() == "low":
		gain = 1
	elif config.get('sensor','gain').lower() == "high":
		gain = 16
	else:
		gain = 1
	sensitivity= float(config.get('sensor','sensitivity'))
	sample_period= float(config.get('sensor','sample_period'))
	sample_rate= float(config.get('sensor','sample_rate'))
	poll_interval = int(config.get('sensor','poll_interval'))
	consecutive_events = int(config.get('sensor','consecutive_events'))
	event_clear = int(config.get('sensor','event_clear'))
	repeat_alert_timer = int(config.get('sensor','repeat_alert_timer')) * 60
	
	sendto= config.get('alertsender','sendto')
	addr_from= config.get('alertsender','addr_from')
	subject= config.get('alertsender','subject')
	body= config.get('alertsender','body')
	smtp_server= config.get('alertsender','smtp_server')
	smtp_user= config.get('alertsender','smtp_user')
	smtp_password= config.get('alertsender','smtp_password')

	tsl=TSL2561(i2c_address)


	total_samples = sample_period * sample_rate
	num_events = 0
	no_events = 0
	alert_sent = False
	alert_time = time
	
	try:
		while True:
			samples = []
			for period in range(0,int(total_samples)):
				#print tsl.readLux(gain)
				samples.append(tsl.readLux(gain))
				sleep(1 / sample_rate)

			variance_value = variance(samples)
			if variance_value > sensitivity:
				print "Blink Detected, variance is " + str(variance_value)
				num_events += 1
				if num_events >= consecutive_events:
					if alert_sent == False:
						#CALL SEND ALERT
						alert_sent == True
						alert_time = time
					elif time - alert_time >= repeat_alert_timer:
						alert_time = time
					
					
			else:
				print "Ambient, variance is: " + str(variance_value)
			#print "Variance: " + str(variance(samples))
			
				num_events = 0
			

			
			
			
			sleep(poll_interval)

			
	except KeyboardInterrupt:
		print "exited"
		