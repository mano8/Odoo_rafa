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
        "vendor": "0x0d3a",
        "product": "0x0368",
        "name": "Posiflex PP6800",
        "key": "PP6800",
        "type": DeviceType.PRINTER,
        "port_type": DevicePortType.SERIAL,
        "conf": {
            "devfile": "/dev/ttyACM0",
            "baudrate": 115200,
            "bytesize": 8,
            "parity": "N",
            "stopbits": 1,
            "timeout": 2,
            "dsrdtr": False,
            # TM-T88IV: generic 80mm/203-DPI ESC/POS receipt profile (PP6800 is compatible)
            "profile": "TM-T88IV",
        },
        # PP-6800: 80mm paper, 203 DPI. Physical printable width observed as
        # ~512 dots (64mm); 576 clips the right ~8mm of content.
        "print_width": 512,
        "image_conf": {
            # bitImageColumn (ESC *) instead of bitImageRaster (GS v 0):
            # PP6800 firmware silently drops GS v 0 raster data past ~2
            # fragments (~480 rows) regardless of fragment_height tuning.
            "impl": "bitImageColumn",
            "center": False,
            # High-density mode (m=33, 24-pin) causes horizontal blank lines
            # on the PP6800 thermal head — single density (m=0) is safer.
            "high_density_vertical": False,
            "high_density_horizontal": False,
        },
    },
]
