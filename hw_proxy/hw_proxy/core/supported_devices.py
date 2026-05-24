"""Supported Printer Devices"""

from enum import Enum


class DeviceType(Enum):
    """Printer Device type"""
    PRINTER = "printer"
    CASH_DRAWER = "cash_drawer"


class DevicePortType(Enum):
    """Printer Device type"""
    USB = "usb"
    NETWORK = "network"
    SERIAL = "serial"


device_list = [
    {
        'vendor': "0x0d3a",
        'product': "0x0368",
        'name': 'Posiflex PP6800',
        'key': 'PP6800',
        'type': DeviceType.PRINTER,
        'port_type': DevicePortType.SERIAL,
        'conf': {
            "devfile": "/dev/ttyACM0",
            "baudrate": 115200,  # 115200,
            "bytesize": 8,
            "parity": 'N',
            "stopbits": 1,
            "timeout": 2,
            "dsrdtr": False,
            "profile": "TM-L90"
        },
        # PP-6800: 80mm paper at 203 DPI; printable width ≈ 512–576 dots — tune if output is clipped or padded
        'print_width': 512,
        'image_conf': {
            "impl": "bitImageRaster",
            "fragment_height": 256,
            "center": False,
        }
    },
]
