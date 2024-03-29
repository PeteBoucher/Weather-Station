#*********************************************************************
#*
#* $Id: yocto_voltage.py 15257 2014-03-06 10:19:36Z seb $
#*
#* Implements yFindVoltage(), the high-level API for Voltage functions
#*
#* - - - - - - - - - License information: - - - - - - - - - 
#*
#*  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
#*
#*  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
#*  non-exclusive license to use, modify, copy and integrate this
#*  file into your software for the sole purpose of interfacing
#*  with Yoctopuce products.
#*
#*  You may reproduce and distribute copies of this file in
#*  source or object form, as long as the sole purpose of this
#*  code is to interface with Yoctopuce products. You must retain
#*  this notice in the distributed source file.
#*
#*  You should refer to Yoctopuce General Terms and Conditions
#*  for additional information regarding your rights and
#*  obligations.
#*
#*  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
#*  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING 
#*  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
#*  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
#*  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
#*  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
#*  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR 
#*  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT 
#*  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
#*  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
#*  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
#*  WARRANTY, OR OTHERWISE.
#*
#*********************************************************************/


__docformat__ = 'restructuredtext en'
from yocto_api import *


#--- (YVoltage class start)
#noinspection PyProtectedMember
class YVoltage(YSensor):
    """
    The Yoctopuce application programming interface allows you to read an instant
    measure of the sensor, as well as the minimal and maximal values observed.
    
    """
#--- (end of YVoltage class start)
    #--- (YVoltage return codes)
    #--- (end of YVoltage return codes)
    #--- (YVoltage definitions)
    #--- (end of YVoltage definitions)

    def __init__(self, func):
        super(YVoltage, self).__init__(func)
        self._className = 'Voltage'
        #--- (YVoltage attributes)
        self._callback = None
        #--- (end of YVoltage attributes)

    #--- (YVoltage implementation)
    def _parseAttr(self, member):
        super(YVoltage, self)._parseAttr(member)

    @staticmethod
    def FindVoltage(func):
        """
        Retrieves a voltage sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>
        
        This function does not require that the voltage sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YVoltage.isOnline() to test if the voltage sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a voltage sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.
        
        @param func : a string that uniquely characterizes the voltage sensor
        
        @return a YVoltage object allowing you to drive the voltage sensor.
        """
        # obj
        obj = YFunction._FindFromCache("Voltage", func)
        if obj is None:
            obj = YVoltage(func)
            YFunction._AddToCache("Voltage", func, obj)
        return obj

    def nextVoltage(self):
        """
        Continues the enumeration of voltage sensors started using yFirstVoltage().
        
        @return a pointer to a YVoltage object, corresponding to
                a voltage sensor currently online, or a None pointer
                if there are no more voltage sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YVoltage.FindVoltage(hwidRef.value)

#--- (end of YVoltage implementation)

#--- (Voltage functions)

    @staticmethod
    def FirstVoltage():
        """
        Starts the enumeration of voltage sensors currently accessible.
        Use the method YVoltage.nextVoltage() to iterate on
        next voltage sensors.
        
        @return a pointer to a YVoltage object, corresponding to
                the first voltage sensor currently online, or a None pointer
                if there are none.
        """
        devRef = YRefParam()
        neededsizeRef = YRefParam()
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        errmsgRef = YRefParam()
        size = YAPI.C_INTSIZE
        #noinspection PyTypeChecker,PyCallingNonCallable
        p = (ctypes.c_int * 1)()
        err = YAPI.apiGetFunctionsByClass("Voltage", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YVoltage.FindVoltage(serialRef.value + "." + funcIdRef.value)

#--- (end of Voltage functions)
