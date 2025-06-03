"""
hw_proxy module Exceptions
"""


class HwProxyError(Exception):
    """HwProxyError from hw_proxy app"""


class HwHardwareError(HwProxyError):
    """HwDeviceError from device configuration"""


class HwDeviceError(HwProxyError):
    """HwDeviceError from device configuration"""


class HwPrinterError(HwDeviceError):
    """HwPrinterError from printer device"""


class HwEscPosError(HwPrinterError):
    """HwEscPosError from printer device escpos"""