# -*- coding: utf-8 -*-
#
# Software License Conditions
# ---------------------------
# All license information can be found in the following docstring of the module.
#
# Hint for editing this source code:
# ----------------------------------
#
# As there is a lot of documentation text here, please configure your code editing
# software for automatic line feed for long lines. This is more simple than to
# correct manual line feeds during changing of documentations texts.
#
# Frank
# (fherb2 @ github.com)
#
"""Python module: z21client
===========================

Introduction
------------

This module implements communication with the Roco/Fleischmann Z21 central station and compatible devices.

It based on the published "Z21 LAN Protocol Specification", V1.13 (EN), by Roco/Fleischmann, downloaded from https://www.z21.eu/en/downloads/manuals at 3.12. 2023 by using the link https://www.z21.eu/media/Kwc_Basic_DownloadTag_Component/root-en-main_47-1652-959-downloadTag-download/default/d559b9cf/1699290380/z21-lan-protokoll-en.pdf. This document can not be part of these development repository since the copyright policy in this document.

Differences between the identifiers in the protocol specification and the identifiers used here
-----------------------------------------------------------------------------------------------

While the "Z21 LAN Protocol Specification" document only introduces identifiers for communication between the devices and the central station, in this Python module we are also dealing with identifiers for data and functions at a higher level of abstraction.

The communication methods for a Z21 client is summarized in the class:

    * `Z21Client`.

Used identifiers and structures in "Z21 LAN Protocol Specification" are collected here in two classes:

    * `SndMsg` and 
    * `RcvMsg`

Z21-LAN message identifiers, like LAN_GET_SERIAL_NUMBER will be used here identically with the exception of the first 4 letters. Using this class as instance, these 4 letters will be replaced by users class object name. So, as a example, the message name "LAN_GET_SERIAL_NUMBER" changes to "myZ21SndMsgObject.GET_SERIAL_NUMBER" as constant value to specify the special message and "myZ21SndMsgObject.get_serial_number()" as function call to process these message.

Conceptual state:
-----------------
Full conceptual development process in progress: The content and interfaces can still change considerably.

##########################################################

License
=======

Used License: MIT License

Defining copyrights (c) and license conditions, fundamental author of this file:
Dr.-Ing. Frank Herbrand
e-mail: herbrand at gmx.de 
github.com user: fherb2

I, Frank Herbrand, hereby grant the license for further use in the form of the generally known MIT license, which was published in 2023 at the following location: https://de.wikipedia.org/wiki/MIT-Lizenz in the form specified by this site at that time:

Copyright (c) 2023 Dr.-Ing. Frank Herbrand

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# #################################################################################################
#                                                                                                 #
# Imports                                                                                         #
# -------                                                                                         #
#                                                                                                 #
# Typing
# ......
#
# Of course, Python doesn't check any typing. But to avoid mistakes and prepare compatibility to
# PyPi, typing is part of the source here and a good feature to deliver good quality software.
# 
from typing import Any
#
try:
    from collections.abc import Callable
except:
    from typing import Callable # for Python < 3.9
#
import time
import asyncio
import socket
from enum import Enum
from enum import auto as enum_auto
from dataclasses import dataclass

#                                                                                                 #
#                                                                                                 #
# #################################################################################################
    

# #################################################################################################
#                                                                                                 #
# Module main class: The Z21Client                                                                #
# ================================                                                                #
#                                                                                                 #
class Z21Client:
    """z21 main class
    =================
    For some basic information about the module and the classes, please, read the module documentation.

    Conceptual state: The content and interfaces can still change considerably.
    """
    # #############################################################################################
    #                                                                                             #
    # INITIALIZER                                                                                 #
    # -----------                                                                                 #
    #                                                                                             #
    def __init__(self):
        """Creator of the z21 client class
        ----------------------------------
        Conceptual state: The content and interfaces can still change considerably.
        """
        # #########################################################################################
        #                                                                                         #
        # Receive Data Household                                                                  #
        # ......................                                                                  #
        self.rcvData = {
            """ Holds the last value received from Z21
            ------------------------------------------
            Values with value `None` are not yet initialized resp. waiting for a new requested actualizing.
            
            To get an actualized value, send the related request and wait until the value is not more `None`. By sending the request the last value of the requested value will be set to `None`. So, the non-`None` state is the signal that this value is actualized related to the last request.
            """
            "serial_number":  None, 
            "lock_code": None,
            "hw_type_fw_version": None,
            "turnout_state": None # memorized as dictionary with elements:    address_number: state
            
            # TODO: Add all other values
            }
        #
        #
        # Structure to call the right data stream processing function depending headers automatically
        # ...........................................................................................        
        self.MSG_STRUC:dict = {
            0x10:   {"name": "GET_SERIAL_NUMBER",   "callback": self._cb_uint32_le, "variable": "serial_number"},
            0x18:   {"name": "GET_CODE",            "callback": self._cb_lock_code, "variable": "lock_code"},
            0x1A:   {"name": "GET_HWINFO",          "callback": self._cb_hw_sw, "variable": "hw_type_fw_version"},
            0x40:   {
                0x43: {"name": "X_TURNOUT_INFO",    "callback": self._cb_actualize_turnout_state, "variable": "turnout_state"},
                0x44: {"name": "X_EXT_ACCESSORY_INFO", "callback": self._cb_dummy, "variable": "serial_number"},
                0x61: {
                    0x00: {"name": "X_BC_TRACK_POWER_OFF",  "callback": self._cb_dummy, "variable": "serial_number"},
                    0x01: {"name": "X_BC_TRACK_POWER_ON",   "callback": self._cb_dummy, "variable": "serial_number"}
                    }
                }
            }
        #
        #
        #
        self.rcv_data = self.rcvData()
        self.shut_down_event = asyncio.Event()
        self.udp_listener_task = asyncio.create_task(self.udp_rcv_task())
        
        # TODO: a lot of work


        #                                                                                          #
        # ##########################################################################################
    #                                                                                              #
    #                                                                                              #
    # ##############################################################################################
        

    # ##############################################################################################
    #                                                                                              #
    # Data stream processing callback functions for self.MSG_STRUC                                 #
    # ------------------------------------------------------------                                 #
    #                                          
    def _cb_dummy(self, data_bytes:bytes, variable:str=None):
        """Does nothing. But eat the data bytes."""
        pass
    #
    def _cb_uint32_le(self, data_bytes:bytes, variable:str):
        """Convert 32 bits in little endian to integer."""
        self.rcvData[variable] = int.from_bytes(data_bytes[:4], byteorder='little')
    #
    def _cb_lock_code(self, data_bytes:bytes, variable:str):
        """Special replay to the locking of the central station
        -------------------------------------------------------
        Z21 start can be locked. This converts the lock state into a meaningful string."""
        means = {
            0x00: "Z21_NO_LOCK.  All features permitted",
            0x01: "z21_START_LOCKED. „z21 start”: driving and switching is blocked",
            0x02: "z21_START_UNLOCKED. „z21 start”: driving and switching is permitted"
        }
        self.rcvData[variable] = means[data_bytes[0]]
    #
    def _cb_hw_sw(self, data_bytes:bytes, variable:str):
        """Special reply to the Hardware and Firmware version numbers"""
        hw = int.from_bytes(data_bytes[:4], byteorder='little')
        sw = bcd_decode(data_bytes[4:], decimals = 2)
        self.rcvData[variable] = f"Hardware-Version: {hw}, Software-Version: {sw}"
    #
    def _cb_actualize_turnout_state(self, data_bytes:bytes, variable:str):
        address = int.from_bytes(data_bytes[:2], byteorder='big')
        value   = int.from_bytes(data_bytes[2])
        variable[address]: value
    #                                                                                              #
    #                                                                                              #
    # ##############################################################################################
        

    # ##############################################################################################
    #                                                                                              #
    # Data stream processing                                                                       #
    # ......................                                                                       #
    #                                                                                              #
    def _process_dataset(self, dataset_header:int, dataset_data:bytes):
        # Since the Z21 API we can different levels of structured data.
        # Following we crawl this structure and call the right callback method
        # with the rest of data:
        if dataset_header not in self.MSG_STRUC:
            raise ValueError(f"Receive a Z21 Dataset with unknown header value.")
        structure = self.MSG_STRUC[dataset_header]
        if "name" not in structure:
            # a sub-header (x-header) is following
            sub_header = int.from_bytes(dataset_data[:2], byteorder='little')
            if len(dataset_data) > 2:
                dataset_data = dataset_data[2:]
            else:
                dataset_data = None
            if sub_header not in structure:
                raise ValueError(f"Receive a Z21 Dataset with unknown x-header value.")
            sub_structure = structure[sub_header]
            if "name" not in sub_structure:
                # a sub-sub-header (DB0) is following
                sub_sub_header = int.from_bytes(dataset_data[:1], byteorder='little')
                if sub_sub_header not in sub_structure:
                    raise ValueError(f"Receive a Z21 Dataset with unknown x-header value.")
                if len(dataset_data) > 1:
                    dataset_data = dataset_data[1:]
                else:
                    dataset_data = None
                sub_sub_header["callback"](dataset_data, sub_sub_header["variable"])
            else:
                sub_header["callback"](dataset_data, sub_sub_header["variable"])
        else:
            dataset_header["callback"](dataset_data, sub_sub_header["variable"])
    #                                                                                              #
    #                                                                                              #
    # ##############################################################################################
      
        
    # ##############################################################################################   
    #                                                                                              #
    # UDP Listener task as async process to be compatible with micro-controllers                   #
    # --------------------------------------------------------------------------                   #
    #                                                                                              #
    # stop signal from main program
    async def stop(self):
        self.shut_down_event.set() # say udp listener task to finish
        await asyncio.sleep(0.2) # give CPU time to the task to can finish
    #
    # UDP Listener task function   
    async def udp_rcv_task(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socked created")
        sock.settimeout(0.001)
        sock.bind(("127.0.0.1", 21105))
        while not self.shut_down_event.is_set():
            try:
                sock.recv(1_000)
                print("NO TIMEOUT")
            except OSError as err:
                if str(err) != "timed out":
                    break
            await asyncio.sleep(0.1) # get back some 
        sock.close()
        print("Socked closed")
    #                                                                                       #
    # #######################################################################################
            
    
    
    
        
        

    def _proc_rcv_stream(self, udp_data_stream:bytes) -> None:
        # One stream can contain more than one Z21 Dataset! So our stream mus be processed as loop.
        stream = udp_data_stream.copy()
        while len(stream) >= 4: # Z21 Dataset must be at least 4 bytes long
            dataset_length = int.from_bytes(stream[:2], byteorder='little')
            if dataset_length > len(stream):
                raise ValueError(f"Length information in Z21 answer is wrong. Byte 0 and 1 say length={dataset_length}, but Z21 Dataset length={len(stream)}")
            dataset_header = int.from_bytes(stream[2:4], byteorder='little')
            dataset_data = stream[4:dataset_length]
            stream = stream[dataset_length:]
            self._process_dataset(dataset_header, dataset_data)
            

    #                                                                                          #
    # ##########################################################################################
    
    
    
    # ##########################################################################################
    #                                                                                          #
    # MESSAGES                                                                                 #
    # --------                                                                                 #
    #                                                                                          #
    @dataclass
    class snd:
        def get_serial_number(self):
            self.send(0x10)
        def get_code(self):
            self.send(0x18)
        def get_hwinfo(self):
            self.send(0x1A)
        def logoff(self):
            self.send(0x30)
        def x_get_version(self):
            self.send(0x40, 0x21, 0x21)
        def x_get_status(self):
            self.send(0x40, 0x21, 0x24)
        def x_set_track_power_off(self):
            self.send(0x40, 0x21, 0x80)
        def x_set_track_power_on(self):
            self.send(0x40, 0x21, 0x81)
        def x_dcc_read_register(self, register:int):
            self.send(0x40, 0x22, 0x11, register)
        def x_cv_read(self, cv_address:int):
            self.send(0x40, 0x23, 0x11, cv_address)
        def x_dcc_write_register(self, register:int, value:int):
            self.send(0x40, 0x23, 0x11, (register, value))
        def x_cv_write(self, cv_address:int, value:int):
            self.send(0x40, 0x24, 0x12, (cv_address, value))
        def x_mm_write_byte(self, register:int, value:int):
            self.send(0x40, 0x24, 0xFF, (register, value))
        def x_get_turnout_info(self, turnout_address:int):
            self.send(0x40, 0x43, data=(turnout_address))
            
         
            
                                
    #                                                                                          #
    # ##########################################################################################
    
    def send(self,
             header:int,
             x_header:(int|None)   = None,
             db0:(int|None)        = None,
             data:Any                   = None
            ):
        pass
    
#                                                                                                 #
#                                                                                                 #
#                                                                                                 # 
###################################################################################################




# #################################################################################################
#                                                                                                 #
# Class for send messages to a z21 central station                                                #
# ================================================                                                #
#                                                                                                 #
class SndMsg:
    """Class SndMsg is a template for all message what we, as client, can send to a Z21 central station.
    ----------------------------------------------------------------------------------------------------
    """
    def __init__(self,
                    name:          str,        # Name of the message as defined in Z21 LAN specification
                    pack_callback: Callable,   # function (pointer) to pack given data of a message as data stream
                    header:        int,        # header of message
                    sub_header:    (int|None) = None, # in case there is a sub header like X-Header (4 Byte)
                    db0:           (int|None) = None, # in case there is a fix data byte 0 (1 byte) 
                    ):
        self._name:str                  = name
        """str: Name of the message as defined in Z21 LAN specification without the part 'LAN_'."""
        self._pack_callback:Callable    = pack_callback
        """Callable: Function what converts data of the message into a byte stream."""
        self._header:int                = header
        """int: Header as defined by Z21 documentation."""
        self._dataset_data:(bytes|None) = None
        """bytes: data of a Z21 dataset transformed to a byte stream"""
        self._sub_header:(int|None)     = sub_header
        """int: Special Z21 messages has a second header specifier inside the data specified by the main header."""
        self._db0:(int|None)            = db0
        """int: Some less messages have a third level specifier for the message named DB0."""
        self._last_data:(bytes|None)    = None  # last sent data
        """bytes: After call of 'stream(data:Any)' what calculates and give back a byte stream containing data, '_last_data' contains the used data."""
    #
    # following, we avoid a direct manipulation of private data by using property functions
    #
    @property
    def name(self) -> str:
        """str: Name of the message as defined in Z21 LAN specification without the part 'LAN_'."""
        return self._name
    @property
    def pack_callback(self) -> Callable:
        """Callable: Function what converts data of the message into a byte stream."""
        return self._pack_callback
    @property
    def header(self) -> int:
        """int: Header as defined by Z21 documentation."""
        return self._header
    @property
    def sub_header(self) -> int:
        """int: Special Z21 messages has a second header specifier inside the data specified by the main header."""
        return self._sub_header
    @property
    def db0(self) -> int:
        """int: Some less messages have a third level specifier for the message named DB0."""
        return self._db0
    @property
    def last_data(self) -> Any:
        """bytes: After call of 'stream(data:Any)' what calculates and give back a byte stream containing data, '_last_data' contains the used data."""
        return self._last_data
    #
    # methods which doesn't need parameters but get values back; will be handled like properties:
    #
    @property 
    def all(self) -> dict:
        """dict: All data of the object collected as dictionary. The datatype and content of the values are identically like a direct access at these data."""
        return {
            "name": self._name,
            "pack_callback": self._pack_callback,
            "header": self._header,
            "sub_header": self._sub_header,
            "db0": self._db0,
            "last_data": self._last_data,
            "last_stream": self.stream(self._last_data)
        }
    #
    # Methods which (really) do data processing
    # -----------------------------------------
    #
    # "to_dataset()"
    # ..............
    def _to_dataset(self):
        """Converts any data stream into a Z21 data set."""
        pass
    #
    # "x_to_data()"
    # .............
    def _x_to_data(self):
        """Converts a Z21 X-Bus data frame into a Z21 data-set data stream.
        -------------------------------------------------------------------
        The result is a data stream, what will be used by _to_dataset() for the completely formatting to send to Z21."""
        pass
    #
    # "loconet_to_data()"
    # ...................
    def _loconet_to_data(self):
        """Converts a Z21 LocoNet data frame into a Z21 data-set data stream.
        -------------------------------------------------------------------
        The result is a data stream, what will be used by _to_dataset() for the completely formatting to send to Z21."""
        pass

    
    
    
    def stream(self, data:Any) -> bytes:
        """byte-stream: all data formatted as a byte stream with little-endian order"""
        self._last_data = data
        byte_stream = (self.header & 0xFFFF).to_bytes(2, 'little')
        if self.sub_header is not None:
            byte_stream = (self.sub_header & 0xFFFF).to_bytes(2, 'little')
        if self.db0 is not None:
            byte_stream += (self.db0 & 0xFF).to_bytes(1, 'little')
        byte_stream += self.pack_callback(data)
        return len(byte_stream).to_bytes(2, 'little') + byte_stream
                                                                                                 #
#                                                                                                 # 
# #################################################################################################




# #################################################################################################
#                                                                                                 #
# Helpers                                                                                         #
# =======                                                                                         #
#                                                                                                 #  

def bcd_decode(data:bytes, decimals:int = 0):
    """Decode a BCD number with decimal point"""
    res = 0
    for n, b in enumerate(reversed(data)):
        res += (b & 0x0F) * 10 ** (n * 2 - decimals)
        res += (b >> 4) * 10 ** (n * 2 + 1 - decimals)
    return res

#                                                                                                 #      
#                                                                                                 # 
# #################################################################################################
  
  
async def main():
    """Only for tests during development"""
    z21 = Z21Client()  
    await asyncio.sleep(15)
    await z21.stop()    
    exit(0)
    
  
if __name__ == '__main__':
    asyncio.run(main())
