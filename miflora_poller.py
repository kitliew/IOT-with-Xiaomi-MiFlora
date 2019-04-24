#!/usr/bin/env python3

import datetime
import subprocess
import time
import sys
import re
from gatttool_ble import char_read, char_write_req
import pandas as pd


#handle number for characteristics
_MI_NAME					= "0x0003"
_MI_BATTERY_AND_VERSION		= "0x0038"	#first byte is battery, remaining 5 byte in ascii format of X.X.X
_MI_SENSOR_DATA				= "0x0035"
_MI_DEVICE_TIME				= "0x0041"	#time since device boot
_MI_HISTORY_READ			= "0x003c"

_MI_SENSOR_CONTROL			= "0x0033"
_MODE_CHANGE				= "A01F"

_MI_HISTORY_CONTROL			= "0x003e"
_MI_HISTORY_READ_INIT		= "A00000"
_MI_HISTORY_READ_SUCCESS	= "A20000"
_MI_HISTORY_READ_FAILED		= "A30000"



#some universal functions
def hex_to_decimal(hex_data):
	return int(hex_data,16)

def hex_to_ascii(hex_data):
	"""Characteristics values (hex) as input and convert to ascii"""
	values = [int(x, 16) for x in hex_data.split()]		#convert to decimal
	return "".join(chr(x) for x in values)

def little_endian(hex_data, byte_start, byte_end = None):
	if byte_end != None and byte_start == 0:
		byte_start = None
		result = "".join(hex_data.split()[byte_end::-1])
	elif byte_end != None and byte_start > 0:
		result = "".join(hex_data.split()[byte_end:byte_start-1:-1])
	else:
		result = "".join(hex_data.split()[byte_start])
	return(result)

def hex_to_time(hex_data, byte_start = 0, byte_end = 3):
	selected_hex = little_endian(hex_data, byte_start, byte_end)
	hex_time = datetime.datetime.utcfromtimestamp(hex_to_decimal(selected_hex))
	return hex_time


class MiFlora(object):
	"""
	Xiaomi MiFlora device
	"""

	def __init__(self, mac):
		self.mac = mac

	def name(self):
		"""Return name of device"""
		hex_data = char_read(self.mac, _MI_NAME)
		return hex_to_ascii(hex_data)

	def hardware_version(self):
		"""Return hardware_version running in device"""
		hex_data = char_read(self.mac, _MI_BATTERY_AND_VERSION)
		return hex_to_ascii(hex_data[6:])

	def battery_level(self):
		"""Return current battery level"""
		hex_data = char_read(self.mac, _MI_BATTERY_AND_VERSION)
		return hex_to_decimal(hex_data[0:2])

	def sensor_data(self):
		"""Return 4 sensor data. Temperature, Brightness, Moisture, Conductivity"""
		char_write_req(self.mac, _MI_SENSOR_CONTROL, _MODE_CHANGE)
		hex_data = char_read(self.mac, _MI_SENSOR_DATA)
		print(hex_data)
		return MiTranslation(hex_data)

	def history_data(self):
		"""Return a list of history readings from 4 sensors"""			#history read only have 8sec window
		char_write_req(self.mac, _MI_HISTORY_CONTROL, _MI_HISTORY_READ_INIT)
		history_summary = char_read(self.mac, _MI_HISTORY_READ)
		hours_of_history = hex_to_decimal(history_summary[:2])
		history=[]
		for i in range(hours_of_history):
			i_to_bytes = i.to_bytes(2, "little")						#little endian format/bytes is neat. change int to bytes(2 byte, "little" endian format)
			i_to_hex = i_to_bytes.hex()
			char_write_req(self.mac, _MI_HISTORY_CONTROL, "a1" + i_to_hex)
			history_hex = char_read(self.mac, _MI_HISTORY_READ)			#data received
			history.append(history_hex)
		return history

	def _epoch_time(self):
		'''Return the device epoch (boot) time'''
		current_time = time.time()
		device_time = char_read(_MI_DEVICE_TIME)
		time_dff = current_time - device_time
		return current_time, device_time, time_dff

class MiTranslation(object):
	"""
	Translate MiFlora device 16bytes hex code into readable values.
	Hex to decimal (little endian).

	Bytes, Sensors:
	byte 0-1	: Temperature 				in (X*0.1) °C
	byte 2		: Unknown
	byte 3-6	: Brightness/sunlight		in lux
	byte 7		: Moisture					in %
	byte 8-9	: Conductivity/Fertility	in µS/cm
	byte 10-15	: Assume going to some handle? Probably history record?
	byte 10		: Char properties
	byte 11		: Handle
	byte 12-15	: Partial UUID 9b34fb
	"""
	def __init__(self, hex_data):
		self.temperature	= hex_to_decimal(little_endian(hex_data,0,1)) * 0.1
		self.brightness		= hex_to_decimal(little_endian(hex_data,3,6))
		self.moisture		= hex_to_decimal(little_endian(hex_data,7))
		self.conductivity	= hex_to_decimal(little_endian(hex_data,8,9))


class HistoryTranslate(object):
	"""
	Translate MiFlora device 16bytes hex code into readable values.
	Hex to decimal (little endian).

	Bytes, Sensors:
	byte 0-1	: Temperature 				in (X*0.1) °C
	byte 2		: Unknown
	byte 3-6	: Brightness/sunlight		in lux
	byte 7		: Moisture					in %
	byte 8-9	: Conductivity/Fertility	in µS/cm
	byte 10-15	: Assume going to some handle? Probably history record?
	byte 10		: Char properties
	byte 11		: Handle
	byte 12-15	: Partial UUID 9b34fb
	"""
	def __init__(self, hex_data):
		self.temperature = hex_to_decimal(little_endian(hex_data,0,1)) * 0.1
		self.brightness = hex_to_decimal(little_endian(hex_data,3,6))
		self.moisture = hex_to_decimal(little_endian(hex_data,7))
		self.conductivity = hex_to_decimal(little_endian(hex_data,8,9))
