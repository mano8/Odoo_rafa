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
        # PP-6800: 80mm paper, 203 DPI. Odoo renders receipts at 512px wide.
        # Resizing up to 576 increases payload from ~84 KB to ~107 KB; the
        # PP6800 firmware silently drops data past its ~90 KB job buffer,
        # truncating the bottom of the receipt.  Keep at 512 (no resize needed).
        "print_width": 512,
        "image_conf": {
            # bitImageColumn (ESC *) instead of bitImageRaster (GS v 0):
            # PP6800 firmware silently drops GS v 0 raster data past ~2
            # fragments (~480 rows) regardless of fragment_height tuning.
            "impl": "bitImageColumn",
            "center": False,
            # m=32 (high_density_vertical=True, high_density_horizontal=False):
            # 24-dot strips with correct paper advance per strip on a 203 DPI
            # head.  m=0 (high_density_vertical=False) uses wrong line spacing
            # → each 8-dot strip followed by a default ~34-dot line feed →
            # "zoomed characters, only top portion visible" symptom.
            # high_density_horizontal=False avoids double-column density that
            # saturates the PP6800 thermal head → horizontal blank-line artifacts.
            "high_density_vertical": True,
            "high_density_horizontal": False,
        },
    },
]
