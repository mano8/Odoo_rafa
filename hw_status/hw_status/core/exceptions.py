"""
hw_status module Exceptions
"""


class HwProxyError(Exception):
    """HwProxyError from hw_status app"""


class HwDeviceError(HwProxyError):
    """HwDeviceError from device configuration"""


class HwPrinterError(HwDeviceError):
    """HwPrinterError from printer device"""


class HwEscPosError(HwPrinterError):
    """HwEscPosError from printer device escpos"""