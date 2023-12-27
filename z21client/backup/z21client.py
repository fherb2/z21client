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
"""Python Package and main class: z21client
===========================================

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
from functools import partial
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
from dataclasses import dataclass, field
from parts.z21dataTemplates import Z21_PARAMETER
from parts.z21dataTemplates import DataNames, RcvMsgName, SndMsgName
from parts.z21dataTemplates import MSG_TO_Z21_STRUC, MSG_FOM_Z21_STRUC

#                                                                                                 #
#                                                                                                 #
# #################################################################################################

# #############################################################################################
#                                                                                             #
# Async UDP Transport     
# ................... 
# see https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-server   
#                                          
#
class Udp_transport_worker:
    # see for UDP listener: https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-server
    def __init__(self, data_processor:Callable=None):
        self.data_processor = data_processor
        self.transport = None
        
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        if self.data_processor is not None:
            self.data_processor(data, addr)

    def error_received(exc):
        pass
        
async def udp_async_creator(data_processor:Callable) -> asyncio.DatagramTransport:
    loop = asyncio.get_running_loop()
    print(type(loop))
    exit(0)
    transport= await loop.create_datagram_endpoint(
                                        protocol_factory = lambda: Udp_transport_worker(data_processor),
                                        local_addr=(Z21_PARAMETER.IP_ADDRESSES["OWN"],
                                                    Z21_PARAMETER.UDP_PORT.Z21_UDP_CLIENT_PORTS[0]),
                                        remote_addr=(Z21_PARAMETER.IP_ADDRESSES["Z21_CENTRAL_STATION"],
                                                     Z21_PARAMETER.UDP_PORT.Z21_UDP_SERVER_PORTS[0]),
                                        family = socket.AF_INET
                                    )
    print(type(transport))
    return transport

def udp_sender(udp_endpoint):
    # use: transport.sendto(bytestream)
    # TODO: implementing
    pass

def data_processor():
    print("Data in processing.")
    pass




async def main():
    """Only for tests during development"""
    MESSAGE = b'\x04\x00\x10\x00'
    transport = udp_async_creator(data_processor)
    

    while True:
        asyncio.sleep(1.0)
        
    
  
if __name__ == '__main__':
    asyncio.run(main())










  
    


# #################################################################################################
#                                                                                                 #
# Module main class: The Z21Client                                                                #
# ================================                                                                #
#                                                                                                 #
class Z21Client:
    """z21 main class
    =================
    For some basic information about the module and the classes, please, read the module documentation.
    
    This is the main class for clients to communicate with Roco/Fleischmann Z21 System devices like central stations or boosters.

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
        print("INIT")
        rcv = self.Rcv()
        pass # TODO
    #                                                                                              #
    # ##############################################################################################




    def set_msg_callback(self, msg_struct:dict, name:str, callback_fct:Callable):
        """set_msg_callback includes the right callback function into the message structure of variables containing the structure Z21_DEFINES.MSG_FROM_Z21.STRUCT_TMPL or structure Z21_DEFINES.MSG_TO_Z21.STRUCT_TMPL
        -----------------------------------------------------------------------------------------------------

        Its a recursive function to put a callback function into the right message of the receive or send messages.

        Args:
            msg_struct (dict): The structure containing the callback functions. See structure template in Z21_DEFINES.MSG_FROM_Z21 and Z21_DEFINES.MSG_TO_Z21.
            name (str): Message name defined in Z21_DEFINES.MSG_FROM_Z21.STRUCT_TMPL and Z21_DEFINES.MSG_TO_Z21.STRUCT_TMPL
            callback_fct (Callable): Callback function. Parameter is a byte stream for MSG_FROM_Z21 or a data value for MSG_TO_Z21.
        """
        for key,value in msg_struct.iteritems():
            if isinstance(value, dict):
                self.set_msg_callback(value, name, callback_fct)
            else:
                if key == name:
                    msg_struct[key]["callback"] = callback_fct



    #                                                                                              #
    #                                                                                              #
    # ##############################################################################################


    
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


  


