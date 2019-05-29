#!/usr/bin/env python3

from time import sleep
import requests

from miflora_poller import MiFlora

#Miflora address
device_mac="C4:7C:8D:69:FF:97"


def main():
	while True:
		target_device = MiFlora(device_mac)
		target_data = target_device.sensor_data()
		target_temperature = target_data.temperature

		print("Current temperature: " + str(target_temperature))
		url = "http://192.168.0.15/write-to-database.py?temp="+str(cpu_temp)
		result = requests.get(url)
		if result.status_code == 200:
			print("Recorded Temperature is ", cpu_temp)
			sleep(2)
			print("Writing to Database...")
			sleep(2)
			print("Process finish")
			print("Process Initialized Again \nWaiting for Interrupt...")
		else:
			print("An error has occured.", result.status_code)

if __name__ == "__main__":
	main()


