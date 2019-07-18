#!/usr/bin/env python
# -*- coding: cp1252 -*-
# This code is part of DPA Contest V4 project
# Copyright 2013 Telecom ParisTech

import sys
import os
import threading
import time
import logging
import math
import serial
import argparse
import random
import datetime

from aes import AES
from local_bus import LocalBus

class ARMSerial():
    def __init__(self, serport):
        self.ser = None
        self.port = serport

    def __del__(self):
        self.close()

    def disconnect(self):
        self.close()
            
    def close(self):
        if self.ser != None:
            self.ser.close()
            self.ser = None

    def open(self):
        self.connect()
    
    def connect(self):
        if self.ser == None:
            # Open serial port 
            self.ser = serial.Serial()
            self.ser.port = self.port
            self.bytesize = 8
            self.ser.baudrate = 115200
            self.ser.timeout  = 5     # 3 second timeout
            self.ser.stopbits = serial.STOPBITS_ONE
            self.ser.parity = serial.PARITY_NONE # 'N' #'serial.PARITY_EVEN'
            self.ser.open()

    def send(self, data):
        self.ser.write(bytearray(data))
        return True

    def flush(self):
        self.ser.flush()  

    def read(self):
        self.error = False
        nErr = 0
        while True:
            if nErr > 100:
                self.error = True
                return None
            data = bytearray(self.ser.read(self.ser.inWaiting()))
            if len(data) > 0:
                return data
            time.sleep(0.01)
            nErr += 1


def get_random_bytes(n):
    return map(lambda x: random.randint(0, 255), range(n))

class AESEncryption(object):
    def __init__(self, aes):
        self.serial_port = aes
        self.plaintext = None
        self.ciphertext = bytearray(0)
        self.error = False
        self.TraceCounter = 0

    def init_encryption(self):
        self.serial_port.select(0x1);
        self.serial_port.encdec(self.serial_port.MODE_ENC);
        self.serial_port.key(range(16))
        time.sleep(1)

    def _get_input(self):
        # return [0]*16
        # return [97]*16
        return get_random_bytes(16)

    def perform(self):
        # if(self.TraceCounter % 10 == 0):
        self.plaintext = self._get_input()
        self.serial_port.send(self.plaintext)
        a=[]
        time.sleep(0.07)
        self.ciphertext=self.serial_port.read()
        self.TraceCounter += 1

def append_to_file(filename, data):
    with open(filename, 'a') as f:
        f.write(data)

def __main__():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description="Interface Program with STM32 ARM board KECCAK")
    parser.add_argument('--com_port', default="COM4", type=str, help="the serial port for the board")
    args = parser.parse_args()

    serial_port = ARMSerial(args.com_port)
    serial_port.connect()
    time.sleep(1)

    operation = AESEncryption(serial_port)

    while True:
        print "Waiting to start"
        sys.stdout.flush()
        try:
            start = raw_input()
        except Exception as e:
            pass
        nErr = 0
        while True:
            if nErr > 100:
                logging.error("Max trial exceeds! program exits.")
                exit(1)
            operation.perform()
            if operation.error:
                nErr += 1
                operation.error = False
                time.sleep(0.1)
                continue
            break
        result = list(operation.ciphertext)
        # result = list(operation.ciphertext)
        #result = list(operation.ciphertext)
        print(' '.join(map(lambda b: "%02x"%b, result)))
        sys.stdout.flush()
        # append_to_file(input_filename, bytearray(operation.plaintext))
        # append_to_file(output_filename, operation.ciphertext)

if __name__ == '__main__':
    __main__()
