#!/usr/bin/env python3
import sys
import re
import subprocess

import pandas as pd

#universal code
def char_desc(mac):
    """Same as gatttool --char-desc. Add mac address as argument"""
    cmd = "gatttool --device={} --char-desc".format(mac)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    result = result.decode("utf-8").strip()
    handles=[]
    uuids=[]
    lines = result.split("\n")
    for line in lines:
        handle, uuid = line.split(", ")
        handles.append(handle.split("= ")[-1])
        uuids.append(uuid.split("= ")[-1])
    combine = zip(handles, uuids)
    return list(combine)

def char_read(mac, handle):
    """Same as gatttool --char-read. Add mac address and handle as argument"""
    cmd = "gatttool --device={} --char-read --handle={}".format(mac, handle)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    result = result.decode("utf-8").strip()
    values = result.partition(": ")[-1]
    return values

def char_write_req(mac, handle, value):
    """Same as gatttool --char-write. Add mac address,handle and value as argument"""
    cmd = "gatttool --device={} --char-write-req --handle={} --value={}".format(mac, handle, value)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result = process.communicate()[0]
    result = result.decode("utf-8").strip()
    values = re.search("successfully", result)
    if values:
        print(result)
        return None

#extra for display all char_read
class MACcontent(object):
    def __init__(self, mac):
        self.mac = mac

    def pandatable(self):
        """
        Return a DataFrame.
        """
        pandatable = pd.DataFrame(char_desc(self.mac), columns = ["Handles", "UUIDs"])
        pandatable["Values"] = [(char_read(self.mac,x)) for x in pandatable["Handles"]]
        pandatable.set_index("Handles", inplace=True)
        return(pandatable)
