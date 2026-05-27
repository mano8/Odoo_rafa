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
            "baudrate": 115200,
            "bytesize": 8,
            "parity": 'N',
            "stopbits": 1,
            "timeout": 2,
            "dsrdtr": False,
            # TM-T88IV: generic 80mm/203-DPI ESC/POS receipt profile (PP6800 is compatible)
            "profile": "TM-T88IV"
        },
        # PP-6800: 80mm paper, 203 DPI, 72mm printable = 576 dots.
        # Check hw_proxy INFO logs after first print to confirm Odoo image width and adjust here.
        'print_width': 576,
        'image_conf': {
            "impl": "bitImageColumn",
            "center": False,
        }
    },
]
