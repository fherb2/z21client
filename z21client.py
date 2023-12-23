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

#                                                                                                 #
#                                                                                                 #
# #################################################################################################

@dataclass
class Z21_DATASET:
    """Definitions, structures and templates associated with the Roco/Fleischmann Z21 Systems
    -----------------------------------------------------------------------------------------
    This data class contains a series of definitions and templates for communication.
    
    What is directly defined when creating an instance of this class can be used as it is. However, some data are preconfigured templates, such as the sub-class 'MSG_TO_Z21'. Such templates are preconfigured and must still be filled in by the program before they can be used. In the MSG_TO_Z21 class as an example, the reference to the callback function must be added in this way before this class can be used usefully.
    """
    IP_ADDRESSES:dict = field(default_factory=lambda: {
            "Z21_CENTRAL_STATION": "192.168.0.111"
            })
    """System IP addresses
    ----------------------
    Default is the address of the central station on delivery.
    
    Can and should be expanded with other system devices if part of the full system.
    """
    @dataclass
    class UDP_PORT:
        """Possible usable UDP ports of the Z21-compatible devices
        ----------------------------------------------------------
        Defaults are defined as specified from Roco/Fleischmann.
        
        The values are set in lists so that the range can be extended if necessary.
        """
        Z21_UDP_SERVER_PORTS:list[int] = field(default_factory=lambda:[21105, 21106])
        Z21_UDP_CLIENT_PORTS:list[int] = field(default_factory=lambda:[21105])
    @dataclass
    class MSGs:
        """Special structures in order to automate sending and receiving messages between server and client.
        ----------------------------------------------------------------------------------------------------
        See the extended details by the elements here.
        """
        TO_Z21:dict = field(default_factory=lambda: {
            0x10: {"name": "GET_SERIAL_NUMBER"  , "callback": None, "targetValueName": None},
            0x18: {"name": "GET_CODE"           , "callback": None, "targetValueName": None},
            0x1A: {"name": "GET_HWINFO"         , "callback": None, "targetValueName": None},
            0x30: {"name": "LOGOFF"             , "callback": None, "targetValueName": None},
            0x40: {
                0x21: {
                    0x21: {"name": "X_GET_VERSION"          , "callback": None, "targetValueName": None},
                    0x24: {"name": "X_GET_STATUS"           , "callback": None, "targetValueName": None},
                    0x80: {"name": "X_SET_TRACK_POWER_OFF"  , "callback": None, "targetValueName": None},
                    0x81: {"name": "X_SET_TRACK_POWER_ON"   , "callback": None, "targetValueName": None},
                    },
                0x22: {
                    0x11: {"name": "X_DCC_READ_REGISTER"    , "callback": None, "targetValueName": None},
                    },
                0x23: {
                    0x11: {"name": "X_CV_READ"              , "callback": None, "targetValueName": None},
                    0x12: {"name": "X_DCC_WRITE_REGISTER"   , "callback": None, "targetValueName": None},
                    },
                0x24: {
                    0x12: {"name": "X_CV_WRITE"             , "callback": None, "targetValueName": None},
                    0xFF: {"name": "X_MM_WRITE_BYTE"        , "callback": None, "targetValueName": None},
                    },
                0x43: {"name": "X_GET_TURNOUT_INFO"         , "callback": None, "targetValueName": None},
                0x44: {"name": "X_GET_EXT_ACCESSORY_INFO"   , "callback": None, "targetValueName": None},
                0x53: {"name": "X_SET_TURNOUT"              , "callback": None, "targetValueName": None},
                0x54: {"name": "X_SET_EXT_ACCESSORY"        , "callback": None, "targetValueName": None},
                0x80: {"name": "X_SET_STOP"                 , "callback": None, "targetValueName": None},
                0x92: {"name": "X_SET_LOCO_E_STOP"          , "callback": None, "targetValueName": None},
                0xE3: {
                    0x44: {"name": "X_PURGE_LOCO"       , "callback": None, "targetValueName": None},
                    0xF0: {"name": "X_GET_LOCO_INFO"    , "callback": None, "targetValueName": None},
                    },
                0xE4: {
                    0x10: {"name": "X_SET_LOCO_DRIVE_14STEPS"   , "callback": None, "targetValueName": None},
                    0x12: {"name": "X_SET_LOCO_DRIVE_28STEPS"   , "callback": None, "targetValueName": None},
                    0x13: {"name": "X_SET_LOCO_DRIVE_128STEPS"  , "callback": None, "targetValueName": None},
                    0xF8: {"name": "X_SET_LOCO_FUNCTION"        , "callback": None, "targetValueName": None},
                    0x20: {"name": "X_SET_LOCO_FUNCTION_GROUP_1", "callback": None, "targetValueName": None},
                    0x21: {"name": "X_SET_LOCO_FUNCTION_GROUP_2", "callback": None, "targetValueName": None},
                    0x22: {"name": "X_SET_LOCO_FUNCTION_GROUP_3", "callback": None, "targetValueName": None},
                    0x23: {"name": "X_SET_LOCO_FUNCTION_GROUP_4", "callback": None, "targetValueName": None},
                    0x28: {"name": "X_SET_LOCO_FUNCTION_GROUP_5", "callback": None, "targetValueName": None},
                    0x29: {"name": "X_SET_LOCO_FUNCTION_GROUP_6", "callback": None, "targetValueName": None},
                    0x2A: {"name": "X_SET_LOCO_FUNCTION_GROUP_7", "callback": None, "targetValueName": None},
                    0x2B: {"name": "X_SET_LOCO_FUNCTION_GROUP_8", "callback": None, "targetValueName": None},   
                    0x50: {"name": "X_SET_LOCO_FUNCTION_GROUP_9", "callback": None, "targetValueName": None},
                    0x51: {"name": "X_SET_LOCO_FUNCTION_GROUP_10"   , "callback": None, "targetValueName": None},
                    0x5F: {"name": "X_SET_LOCO_BINARY_STATE"    , "callback": None, "targetValueName": None},
                    },
                0xE6: {
                    0x30: {"name:": "X_CV_POM_WRITE_BYTE"       , "callback":None, "targetValueName":None},
                    0x30: {"name:": "X_CV_POM_WRITE_BIT"        , "callback":None, "targetValueName":None},
                    0x30: {"name:": "X_CV_POM_READ_BYTE"        , "callback":None, "targetValueName":None},
                    0x31: {"name:": "X_CV_POM_ACCESSORY_WRITE_BYTE", "callback":None, "targetValueName":None},
                    0x31: {"name:": "X_CV_POM_ ACCESSORY_WRITE_BIT", "callback":None, "targetValueName":None},
                    0x31: {"name:": "X_CV_POM_ ACCESSORY_READ_BYTE", "callback":None, "targetValueName":None},
                    },
                0xF1: {
                    0x0A: {"name:": "_X_GET_FIRMWARE_VERSION"   , "callback":None, "targetValueName":None},
                    },
                },
            0x50: {"name:": "SET_BROADCASTFLAGS"    , "callback":None, "targetValueName":None},
            0x51: {"name:": "GET_BROADCASTFLAGS"    , "callback":None, "targetValueName":None},
            0x60: {"name:": "GET_LOCOMODE"          , "callback":None, "targetValueName":None},
            0x61: {"name:": "SET_LOCOMODE"          , "callback":None, "targetValueName":None},
            0x70: {"name:": "GET_TURNOUTMODE"       , "callback":None, "targetValueName":None},
            0x71: {"name:": "SET_TURNOUTMODE"       , "callback":None, "targetValueName":None},
            0x81: {"name:": "RMBUS_GETDATA"         , "callback":None, "targetValueName":None},
            0x82: {"name:": "RMBUS_PROGRAMMODULE"   , "callback":None, "targetValueName":None},
            0x85: {"name:": "SYSTEMSTATE_GETDATA"   , "callback":None, "targetValueName":None},
            0x89: {"name:": "RAILCOM_GETDATA"       , "callback":None, "targetValueName":None},
            0xA2: {"name:": "LOCONET_FROM_LAN"      , "callback":None, "targetValueName":None},
            0xA3: {"name:": "LOCONET_DISPATCH_ADDR" , "callback":None, "targetValueName":None},
            0xA4: {"name:": "LOCONET_DETECTOR"      , "callback":None, "targetValueName":None},
            0xC4: {"name:": "CAN_DETECTOR"          , "callback":None, "targetValueName":None},
            0xC8: {"name:": "CAN_DEVICE_GET_DESCRIPTION"    , "callback":None, "targetValueName":None},
            0xC9: {"name:": "CAN_DEVICE_SET_DESCRIPTION"    , "callback":None, "targetValueName":None},
            0xCB: {"name:": "CAN_BOOSTER_SET_TRACKPOWER"    , "callback":None, "targetValueName":None},
            0xCC: {"name:": "FAST_CLOCK_CONTROL"            , "callback":None, "targetValueName":None},
            0xCE: {"name:": "FAST_CLOCK_SETTINGS_GET"       , "callback":None, "targetValueName":None},
            0xCF: {"name:": "FAST_CLOCK_SETTINGS_SET"       , "callback":None, "targetValueName":None},
            0xB2: {"name:": "BOOSTER_SET_POWER"             , "callback":None, "targetValueName":None},
            0xB8: {"name:": "BOOSTER_GET_DESCRIPTION"       , "callback":None, "targetValueName":None},
            0xB9: {"name:": "BOOSTER_SET_DESCRIPTION"       , "callback":None, "targetValueName":None},
            0xBB: {"name:": "BOOSTER_SYSTEMSTATE_GETDATA"   , "callback":None, "targetValueName":None},
            0xD8: {"name:": "DECODER_GET_DESCRIPTION"       , "callback":None, "targetValueName":None},
            0xD9: {"name:": "DECODER_SET_DESCRIPTION"       , "callback":None, "targetValueName":None},
            0xDB: {"name:": "DECODER_SYSTEMSTATE_GETDATA"   , "callback":None, "targetValueName":None},
            0xE8: {
                0x06: {"name:": "ZLINK_GET_HWINFO"  , "callback":None, "targetValueName":None},
                },
            })
        """ Structure to initialize and process outgoing messages
        ---------------------------------------------------------
        It is so far prepared that only the call-back functions need to be added.

        The structure represents the fixed header and subheader/date values of a specific message. At the lowest level of the dictionary you will find a specially defined dictionary::
        
            name (str): The official message name, defined by Roco/Fleischmann.
                        This is used by the sender process to find the right
                        headers, the callback function to process the given data
                        and, in case the message will be answered by a value,
                        the value name to take the response value into the right
                        memory.
            callback (Callback):
                        Must be filled in by the program with a function
                        reference that formats the data for sending.
                        Default to None -> no callback function registered.
            targetValueName (str):
                        If the message is answered with a value, this is the name
                        of the value in which the value from the response is saved
                        as soon as the response has arrived. 
                        This is important here, as the mechanism for recognizing
                        that a request has been answered is done by replacing the
                        value 'None' with the received value. This makes it
                        possible to recognize when the current value has been
                        received after the request has been sent.
                        Default to none -> no response value expected.
        """
        From_Z21:dict = field(default_factory=lambda: {
                0x10: {"name": "SERIAL_NUMBER",   "callback": None, "targetValueName": "serial_number"},
                0x18: {"name": "CODE",            "callback": None, "targetValueName": "lock_code"},
                0x1A: {"name": "HWINFO",          "callback": None, "targetValueName": "hw_type_fw_version"},
                0x40: {
                    0x43: {"name": "X_TURNOUT_INFO",       "callback": None, "targetValueName": "turnout_state"},
                    0x44: {"name": "X_EXT_ACCESSORY_INFO", "callback": None, "targetValueName": "accessory_state_information"},
                    0x61: {
                        0x00: {"name": "X_BC_TRACK_POWER_OFF",     "callback": None, "targetValueName": None},
                        0x01: {"name": "X_BC_TRACK_POWER_ON",      "callback": None, "targetValueName": None},
                        0x02: {"name": "X_BC_PROGRAMMING_MODE",    "callback": None, "targetValueName": None},
                        0x08: {"name": "X_BC_TRACK_SHORT_CIRCUIT", "callback": None, "targetValueName": None},
                        0x12: {"name": "X_CV_NACK_SC",             "callback": None, "targetValueName": None},
                        0x13: {"name": "X_CV_NACK",                "callback": None, "targetValueName": None},
                        0x82: {"name": "X_UNKNOWN_COMMAND",        "callback": None, "targetValueName": None},
                        },
                    0x62: {
                        0x22: {"name": "X_STATUS_CHANGED",         "callback": None, "targetValueName": "state"},
                        },
                    0x63: {
                        0x21: {"name": "X_VERSION",          "callback": None, "targetValueName": "xbus_version_id"},
                        },
                    0x64: {
                        0x14: {"name": "X_CV_RESULT",        "callback": None, "targetValueName": "cv_result"},
                        },
                    0x81: {"name": "X_BC_STOPPED",           "callback": None, "targetValueName": None},
                    0xEF: {"name": "X_LOCO_INFO",            "callback": None, "targetValueName": "loco_information"},
                    0xF3: {
                        0x0A: {"name": "X_FIRMWARE_VERSION", "callback": None, "targetValueName": "Version_bcd"},
                        },
                    },
                0x51: {"name": "BROADCASTFLAGS",             "callback": None, "targetValueName": "broadcast_flags"},
                0x60: {"name": "LOCOMODE",                   "callback": None, "targetValueName": "loco_address_mode"},
                0x70: {"name": "TURNOUTMODE",                "callback": None, "targetValueName": "accessory_decoder_address_mode"},
                0x80: {"name": "RMBUS_DATACHANGED",          "callback": None, "targetValueName": "group_index_feedback_status"},
                0x84: {"name": "SYSTEMSTATE_DATACHANGED",    "callback": None, "targetValueName": "system_state"},
                0x88: {"name": "RAILCOM_DATACHANGED",        "callback": None, "targetValueName": "rail_com_data"},
                0xA0: {"name": "LOCONET_Z21_RX",             "callback": None, "targetValueName": "loco_net_meldung"},
                0xA1: {"name": "LOCONET_Z21_TX",             "callback": None, "targetValueName": "loco_net_meldung"},
                0xA2: {"name": "LOCONET_FROM_LAN",           "callback": None, "targetValueName": "loco_net_meldung"},
                0xA3: {"name": "LOCONET_DISPATCH_ADDR",      "callback": None, "targetValueName": "loco_address_ergebnis"},
                0xA4: {"name": "LOCONET_DETECTOR",           "callback": None, "targetValueName": "type_feedback_address_info"},
                0xC4: {"name": "CAN_DETECTOR",               "callback": None, "targetValueName": "occupancy_message"},
                0xC8: {"name": "CAN_DEVICE_DESCRIPTION",     "callback": None, "targetValueName": "net_id_name"},
                0xCA: {"name": "CAN_BOOSTER_SYSTEMSTATE_CHGD",    "callback": None, "targetValueName": "can_booster_system_state"},
                0xCD: {"name": "FAST_CLOCK_DATA",                 "callback": None, "targetValueName": "fastclock_time"},
                0xCE: {"name": "FAST_CLOCK_SETTINGS_GET",         "callback": None, "targetValueName": "fastclock_settings"},
                0xB8: {"name": "BOOSTER_DESCRIPTION",             "callback": None, "targetValueName": "string"},
                0xBA: {"name": "BOOSTER_SYSTEMSTATE_DATACHANGED", "callback": None, "targetValueName": "booster_system_state"},
                0xD8: {"name": "DECODER_DESCRIPTION",             "callback": None, "targetValueName": "string"},
                0xDA: {"name": "DECODER_SYSTEMSTATE_DATACHANGED", "callback": None, "targetValueName": "decoder_system_state"},
                0xE8: {
                    0x06: {"name": "ZLINK_HWINFO",                "callback": None, "targetValueName": "z_hw_info"},
                    }
                # TODO: a lot of work: expand to the full content
                })
        """ Structure to initialize and process incoming messages
        ---------------------------------------------------------
        It is so far prepared that only the call-back functions need to be added.
        
        The structure represents the fixed header and subheader/date values of a specific message. At the lowest level of the dictionary you will find a specially defined dictionary::
        
            name (str): The official message name, defined by Roco/Fleischmann.
                        This for information purposes only.
            callback (Callback):
                        Must be filled in by the program with a function
                        reference processing the received data stream
                        that decodes the data for receiving.
                        Default to None -> no callback function registered.
            targetValueName (str):
                        Normally a message is answered with a value or is to
                        be interpreted as special information. This is the name
                        of the variable in which the value from the response is
                        stored.       
        """
    
    


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


    # #############################################################################################
    #                                                                                             #
    # Receive Data Household incl. frame processing                                               #
    # .............................................                                               #
    class Rcv:
        """ Rcv contains received data from Z21 server station and all to processes to get these
        ----------------------------------------------------------------------------------------
        """
        def __init__(self):
            self._data = {
                "serial_number":  None, 
                "lock_code": None,
                "hw_type_fw_version": None,
                "turnout_state": None # memorized as dictionary with elements:    address_number: state
                # TODO: Add all other values
                }
            """ Holds the last value received from Z21
            ------------------------------------------
            Values with value `None` are not yet initialized resp. waiting for a new requested actualizing.
            
            To get an actualized value, send the related request and wait until the value is not more `None`. By sending the request the last value of the requested value will be set to `None`. So, the non-`None` state is the signal that this value is actualized related to the last request.
            """
            #
            # Structure to call the right data stream processing function depending headers automatically
            # ...........................................................................................   
            self._MSG_STRUC = Z21_DEFINES.MSG_FROM_Z21.STRUC_TMPL
            """ Structure to process incoming messages
            """
            self._MSG_STRUC[0x10]["callback"] = self._cb_uint32_le
            self._MSG_STRUC[0x18]["callback"] = self._cb_lock_code
            self._MSG_STRUC[0x1A]["callback"] = self._cb_hw_sw
            self._MSG_STRUC[0x40][0x43]["callback"] = self._cb_actualize_turnout_state
            self._MSG_STRUC[0x40][0x44]["callback"] = self._cb_dummy
            self._MSG_STRUC[0x40][0x61][0x00]["callback"] = self._cb_dummy
            self._MSG_STRUC[0x40][0x61][0x01]["callback"] = self._cb_dummy
            # TODO: a lot of work
            #
            #  Start the async task
            self._udp_rcv_task = self.Udp_rcv_task(self._MSG_STRUC, self.data)
        #
        @property
        def data(self):                
            """ Holds the last value received from Z21
            ------------------------------------------
            Values with value `None` are not yet initialized resp. waiting for a new requested actualizing.
            
            To get an actualized value, send the related request and wait until the value is not more `None`. By sending the request the last value of the requested value will be set to `None`. So, the non-`None` state is the signal that this value is actualized related to the last request.
            """
            return self._data
        #
        def reset_date(self, name:str):
            """Sets a date to the state "unknown" (`None`)
            ----------------------------------------------
            This is used by requesting a new value. With a reset, we memorize, that the new and actually value is not yet received.

            Args:
                name (str): Key of the `data` dictionary
            """
            self._data[name] = None   
        #
        def shutdown(self):
            """Command to shut down the UDP listening process
            -------------------------------------------------

            After this no data will be received from the Z21 station. This is used to shut down a process during finishing the application.
            """
            self._udp_rcv_task.stop_task()
        #
        #
        # Data stream processing callback functions for _MSG_STRUC
        # ........................................................
        #                                          
        def _cb_dummy(self, data_bytes:bytes, variable:str=None):
            """Callback function to process incoming data from Z21 station: Does nothing. But eat the data bytes.
            -----------------------------------------------------------------------------------------------------
            """
            pass
        #
        def _cb_uint32_le(self, data_bytes:bytes, variable:str):
            """Callback function to process incoming data from Z21 station: Convert 32 bits in little endian to integer.
            ------------------------------------------------------------------------------------------------------------
            """
            self.rcvData[variable] = int.from_bytes(data_bytes[:4], byteorder='little')
        #
        def _cb_lock_code(self, data_bytes:bytes, variable:str):
            """Callback function to process incoming data from Z21 station: Special replay to the locking of the central station
            --------------------------------------------------------------------------------------------------------------
            Z21 start can be locked. This converts the lock state into a meaningful string."""
            means = {
                0x00: "Z21_NO_LOCK.  All features permitted",
                0x01: "z21_START_LOCKED. „z21 start”: driving and switching is blocked",
                0x02: "z21_START_UNLOCKED. „z21 start”: driving and switching is permitted"
            }
            self.rcvData[variable] = means[data_bytes[0]]
        #
        def _cb_hw_sw(self, data_bytes:bytes, variable:str):
            """Callback function to process incoming data from Z21 station: Special reply to the Hardware and Firmware version numbers
            -------------------------------------------------------------------------------------------------
            """
            hw = int.from_bytes(data_bytes[:4], byteorder='little')
            sw = bcd_decode(data_bytes[4:], decimals = 2)
            self.rcvData[variable] = f"Hardware-Version: {hw}, Software-Version: {sw}"
        #
        def _cb_actualize_turnout_state(self, data_bytes:bytes, variable:str):
            address = int.from_bytes(data_bytes[:2], byteorder='big')
            value   = int.from_bytes(data_bytes[2])
            variable[address]: value
        #
        #
        # Processing an incoming udp stream
        # .................................
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
                        sub_sub_header["callback"](dataset_data, sub_sub_header["targetValueName"])
                    else:
                        sub_header["callback"](dataset_data, sub_sub_header["targetValueName"])
                else:
                    dataset_header["callback"](dataset_data, sub_sub_header["targetValueName"])
        #
        #
        #
        # UDP Listener task as async process to be compatible with micro-controllers
        # ..........................................................................
        #
        class Udp_rcv_task:
            def __init__(self, msg_struct:dict, data:dict):
                print("AAA")
                self._shut_down_event = asyncio.Event()
                self._udp_listener_task = asyncio.create_task(self._task_proc(msg_struct, data))
            #
            # task function   
            async def _task_proc(self, msg_struct:dict, data:dict):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print("Socked created")
                sock.settimeout(0.001)
                sock.bind(("127.0.0.1", Z21_DEFINES.UDP_PORT.Z21_UDP_CLIENT_PORTS[0]))
                while not self._shut_down_event.is_set():
                    try:
                        data = sock.recv(10_000)
                        print(f"Received data: len: {len(data)}")
                        # ############
                        # TODO: This is the place to process the data
                        # ############
                    except OSError as err:
                        if str(err) != "timed out":
                            break
                    await asyncio.sleep(0.1) # get back some 
                sock.close()
                print("Socked closed")
            #
            # stop signal to finish the task
            async def stop_task(self):
                self._shut_down_event.set() # say udp listener task to finish
                await asyncio.sleep(0.2) # give CPU time to the task to can finish
        #
        #                                                                                       #
        # #######################################################################################

    def process_rcv_msg_callback(self, msg_struct:dict, datagram:bytes, variables:dict, msg_stage:int=0):
        """process_rcv_msg_callback select the right callback function depending from the received datagram ant let the callback function run to convert the data in the datagram and put the result in the right variable of the dictionary `variables`.
        ---------------------------------------------------------------------------------------------------------------

        Args::
        
            msg_struct (dict): Special structured dictionary variable.
            datagram (bytes) : received UDP data
            variables (dict) : The variables dictionary to hold the received values.
            msg_stage (int, optional): For recursive use only!. Don't change the value! Defaults to 0.
            
        """
        # run over the header
        if msg_stage < 2:
            # header or x-header -> 2 byte
            header = int.from_bytes(datagram[:2], byteorder='little', signed=False)
            data   = datagram[2:]
        else:
            # DB0 -> 1 byte
            header = int.from_bytes(datagram[:1], byteorder='little', signed=False)
            data   = datagram[1:]
        for key,value in msg_struct.iteritems():
            if key == header:
                if isinstance(value, dict):
                    self.process_rcv_msg_callback(value, data, msg_stage = msg_stage + 1)
                else:
                    # Bingo!
                    # Process the data and put the result into the specified variable of the variables-dictionary
                    variables["targetValueName"] = partial(value["callback"], data)
                    break

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
  
  
import socket 
async def main():
    """Only for tests during development"""
    z21 = Z21Client()
    UDP_IP = "192.168.0.111"
    UDP_PORT = 21105 
    MESSAGE = b'\x04\x00\x10\x00'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", UDP_PORT)) # das ist wichtig: so ist der Sende-Port gleich dem Empfangs-Port (?)
    while True:
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        await asyncio.sleep(15)
        
    await z21.stop()    
    
  
if __name__ == '__main__':
    asyncio.run(main())
