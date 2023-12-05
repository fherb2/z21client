# -*- coding: utf-8 -*-
"""# Main class of the module z21client
===========================================

This module implements communication with the Roco/Fleischmann Z21 central
and compatible devices.

This project based on the Roco published "Z21 LAN Protocol Specification",
V1.13 (EN), downloaded from https://www.z21.eu/en/downloads/manuals at
3.12. 2023 by using the link 
https://www.z21.eu/media/Kwc_Basic_DownloadTag_Component/root-en-main_47-1652-959-downloadTag-download/default/d559b9cf/1699290380/z21-lan-protokoll-en.pdf. This document can not be part of these development repository since the copyright policy in this document.

Z21-LAN message identifiers, like LAN_GET_SERIAL_NUMBER will be used here
identically with the exception of the first 4 letters. Outside the class,
these 4 letters will be placed by the class object name. So the message name
"LAN_GET_SERIAL_NUMBER" changes to "myZ21Object.GET_SERIAL_NUMBER" as constant
value to specify the special message and "myZ21Object.get_serial_number()"
as function call to process these message. Inside the class, of course, 
"self." is used instead "myZ21Object".

Conceptual state:
-----------------

The content and interfaces can still change considerably.

----------------------------------------------------------------------------

License
========

MIT License

Copyright (c) 2023 Frank Herbrand, herbrand at gmx.de (fherb2 at github.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# #################################################################################################
#                                                                                                 #
# Imports                                                                                         #
# -------                                                                                         #
#                                                                                                 #
# .................
# Typing
#
# Of course, Python doesn't check any typing. But to avoid mistakes and prepare
# compatibility to PyPi for future.
# 
# typing has changed from 3.8 to 3.10; 3.9 was a transitional version for typing hints
from typing import Union # to be save for python < 3.10 (so we don't use "type1 | type2")
from typing import Any

try:
    from collections.abc import Callable
except:
    from typing import Callable # for Python < 3.9
    
from enum import Enum
from enum import auto as enum_auto
from enum import auto as enum_unique
# .................
#
# Specials for class developing
from dataclasses import dataclass
#                                                                                                 #
# #################################################################################################
    

# #################################################################################################
#                                                                                                 #
# Module main class                                                                               #
# =================                                                                               #
#                                                                                                 #
class z21Client():
    """z21 main class
    =================
    
    For some basic information about the module and the class, please, read the module documentation.

    Conceptual state: The content and interfaces can still change considerably.
    """
    def __init__(self):
        """Creator of the z21 main class

        Conceptual state: The content and interfaces can still change considerably.
        """
        pass
    
    # ###########################################################################################
    #
    class SndMsg():
        _name:str               = None
        """private, str | None: Name of the message as defined in Z21 LAN specification without the part 'LAN_'."""
        _pack_callback:Callable = None
        """private, Callable | None: Function what converts data of the message into a byte stream."""
        _header:int             = None
        """private, int | None: Header as defined by Z21 documentation."""
        _sub_header:int         = None
        """private, int | None: Special Z21 messages has a second header specifier inside the data specified by the main header."""
        _db0:int                = None
        """private, int | None: Some less messages have a third level specifier for the message named DB0."""
        _last_data              = None
        """private, bytes | None: After call of 'stream(data:Any)' what calculates and give back a byte stream
        containing data, '_last_data' contains the used data."""
        
        
        def __init__(self,
                     name:          str,        # Name of the message as defined in Z21 LAN specification
                     pack_callback: Callable,   # function (pointer) to pack given data of a message as data stream
                     header:        int,        # header of message
                     sub_header:    int = None, # in case there is a sub header like X-Header (4 Byte)
                     db0:           int = None, # in case there is a fix data byte 0 (1 byte) 
                     ):
            # following, we avoid a direct manipulation of private data
            self._name          = name
            self._pack_callback = pack_callback
            self._header        = header
            self._sub_header    = sub_header
            self._db0           = db0
            self._last_data     = None  # last sent data
        
        # following, we avoid a direct manipulation of private data
        @property
        def name(self) -> str:
            return self._name
        @property
        def pack_callback(self) -> Callable:
            return self._pack_callback
        @property
        def header(self) -> int:
            return self._header
        @property
        def sub_header(self) -> int:
            return self._sub_header
        @property
        def db0(self) -> int:
            return self._db0
        @property
        def last_data(self) -> Any:
            return self._last_data

        @property
        def stream(self, data:Any) -> bytes:
            self._last_data = data
            byte_stream = (self.header & 0xFFFF).to_bytes(2, 'little')
            if self.sub_header is not None:
                byte_stream = (self.sub_header & 0xFFFF).to_bytes(2, 'little')
            if self.db0 is not None:
                byte_stream += (self.db0 & 0xFF).to_bytes(1, 'little')
            byte_stream += self.pack_callback(data)
            return len(byte_stream).to_bytes(2, 'little') + byte_stream
        
        @property 
        def all(self) -> dict:
            return {
                "name": self.name(),
                "pack_callback": self.pack_callback(),
                "header": self.header(),
                "sub_header": self.sub_header(),
                "db0": self.db0(),
                "last_data": self._last_data(),
                "last_stream": self.stream(self._last_data)
            }
            
    change following class like class SndMsg()

    class RcvMsg():
        def __int__(self,
                    name:           str,        # Name of the message as defined in Z21 LAN specification
                    unpack_callback:Callable,   # function (pointer) to unpack received data bytes
                    header:         int,        # header of message
                    sub_header:     int = None, # in case there is a sub header like X-Header (4 Byte)
                    db0:            int = None  # in case there is a fix data byte 0 (1 byte)
                    ):
            # following, we avoid a direct manipulation of private data
            self._name              = name
            self._unpack_callback   = unpack_callback
            self._header            = header
            self._sub_header        = sub_header
            self._db0               = db0
            self.date: Any          = None  # last received data
            
        # following, we avoid a direct manipulation of private data
        @property
        
        def save_if_matches(self, stream) -> bool:
            pass

            
            
#                                                                                              # 
################################################################################################

################################################################################################
#                                                                                              #
# Helpers                                                                                      #
# =======                                                                                      #
#                                                                                              #
        
    
    
# maybe we don't need this, but it's a good listing ;-)  
@enum_unique
class SndMsgName(Enum):
    GET_SERIAL_NUMBER               = enum_auto()
    GET_CODE                        = enum_auto()
    GET_HWINFO                      = enum_auto()
    LOGOFF                          = enum_auto()
    X_GET_VERSION                   = enum_auto()
    X_GET_STATUS                    = enum_auto()
    X_SET_TRACK_POWER_OFF           = enum_auto()
    X_SET_TRACK_POWER_ON            = enum_auto()
    X_DCC_READ_REGISTER             = enum_auto()
    X_CV_READ                       = enum_auto()
    X_DCC_WRITE_REGISTER            = enum_auto()
    X_CV_WRITE                      = enum_auto()
    X_MM_WRITE_BYTE                 = enum_auto()
    X_GET_TURNOUT_INFO              = enum_auto()
    X_GET_EXT_ACCESSORY_INFO        = enum_auto()
    X_SET_TURNOUT                   = enum_auto()
    X_SET_EXT_ACCESSORY             = enum_auto()
    X_SET_STOP                      = enum_auto()
    X_SET_LOCO_E_STOP               = enum_auto()
    X_PURGE_LOCO                    = enum_auto()
    X_GET_LOCO_INFO                 = enum_auto()
    X_SET_LOCO_DRIVE                = enum_auto()
    X_SET_LOCO_FUNCTION             = enum_auto()
    X_SET_LOCO_FUNCTION_GROUP       = enum_auto()
    X_SET_LOCO_BINARY_STATE         = enum_auto()
    X_CV_POM_WRITE_BIT              = enum_auto()
    X_CV_POM_WRITE_BYTE             = enum_auto()
    X_CV_POM_READ_BYTE              = enum_auto()
    X_CV_POM_ACCESSORY_WRITE_BYTE   = enum_auto()
    X_CV_POM_ACCESSORY_WRITE_BIT    = enum_auto()
    X_CV_POM_ACCESSORY_READ_BYTE    = enum_auto()
    X_GET_FIRMWARE_VERSION          = enum_auto()
    SET_BROADCASTFLAGS              = enum_auto()
    GET_BROADCASTFLAGS              = enum_auto()
    GET_LOCOMODE                    = enum_auto()
    SET_LOCOMODE                    = enum_auto()
    GET_TURNOUTMODE                 = enum_auto()
    SET_TURNOUTMODE                 = enum_auto()
    RMBUS_GETDATA                   = enum_auto()
    RMBUS_PROGRAMMODULE             = enum_auto()
    SYSTEMSTATE_GETDATA             = enum_auto()
    RAILCOM_GETDATA                 = enum_auto()
    LOCONET_FROM_LAN                = enum_auto()
    LOCONET_DISPATCH_ADDR           = enum_auto()
    LOCONET_DETECTOR                = enum_auto()
    CAN_DETECTOR                    = enum_auto()
    CAN_DEVICE_GET_DESCRIPTION      = enum_auto()
    CAN_DEVICE_SET_DESCRIPTION      = enum_auto()
    CAN_BOOSTER_SET_TRACKPOWER      = enum_auto()
    FAST_CLOCK_CONTROL              = enum_auto()
    FAST_CLOCK_SETTINGS_GET         = enum_auto()
    FAST_CLOCK_SETTINGS_SET         = enum_auto()
    BOOSTER_SET_POWER               = enum_auto()
    BOOSTER_GET_DESCRIPTION         = enum_auto()
    BOOSTER_SET_DESCRIPTION         = enum_auto()
    BOOSTER_SYSTEMSTATE_GETDATA     = enum_auto()
    DECODER_GET_DESCRIPTION         = enum_auto()
    DECODER_SET_DESCRIPTION         = enum_auto()
    DECODER_SYSTEMSTATE_GETDATA     = enum_auto()
    ZLINK_GET_HWINFO                = enum_auto()

@enum_unique
class RcvMsgName(Enum):
    GET_SERIAL_NUMBER               = enum_auto()
    GET_CODE                        = enum_auto()
    GET_HWINFO                      = enum_auto()
    X_TURNOUT_INFO                  = enum_auto()
    X_EXT_ACCESSORY_INFO            = enum_auto()
    X_BC_TRACK_POWER_OFFX           = enum_auto()
    X_BC_TRACK_POWER_ON             = enum_auto()
    X_BC_PROGRAMMING_MODE           = enum_auto()
    X_BC_TRACK_SHORT_CIRCUIT        = enum_auto()
    X_CV_NACK_SC                    = enum_auto()
    X_CV_NACK                       = enum_auto()
    X_UNKNOWN_COMMAND               = enum_auto()
    X_STATUS_CHANGED                = enum_auto()
    X_GET_VERSION                   = enum_auto()
    X_CV_RESULT                     = enum_auto()
    X_BC_STOPPED                    = enum_auto()
    X_LOCO_INFO                     = enum_auto()
    X_GET_FIRMWARE_VERSION          = enum_auto()
    GET_BROADCASTFLAGS              = enum_auto()
    GET_LOCOMODE                    = enum_auto()
    GET_TURNOUTMODE                 = enum_auto()
    RMBUS_DATACHANGED               = enum_auto()
    SYSTEMSTATE_DATACHANGED         = enum_auto()
    RAILCOM_DATACHANGED             = enum_auto()
    LOCONET_Z21_RX                  = enum_auto()
    LOCONET_Z21_TX                  = enum_auto()
    LOCONET_FROM_LAN                = enum_auto()
    LOCONET_DISPATCH_ADDR           = enum_auto()
    LOCONET_DETECTOR                = enum_auto()
    CAN_DETECTOR                    = enum_auto()
    CAN_DEVICE_GET_DESCRIPTION      = enum_auto()
    CAN_BOOSTER_SYSTEMSTATE_CHGD    = enum_auto()
    FAST_CLOCK_DATA                 = enum_auto()
    FAST_CLOCK_SETTINGS_GET         = enum_auto()
    BOOSTER_GET_DESCRIPTION         = enum_auto()
    BOOSTER_SYSTEMSTATE_DATACHANGED = enum_auto()
    DECODER_GET_DESCRIPTION         = enum_auto()
    DECODER_SYSTEMSTATE_DATACHANGED = enum_auto()
    ZLINK_GET_HWINFO                = enum_auto()

        
#                                                                                              # 
################################################################################################
  