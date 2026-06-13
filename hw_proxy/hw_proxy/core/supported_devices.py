"""Supported Printer Devices"""

import os
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
            # m=33 (both high_density=True): matches python-escpos default and
            # the original working state.  high_density_horizontal=False (m=32)
            # doubles the physical column width on PP6800 → image prints at
            # 2× paper width → "bigger image in smaller support, malformed".
            # high_density_horizontal=True restores native 203 DPI column pitch.
            "high_density_vertical": True,
            "high_density_horizontal": True,
        },
    },
    {
        # Network-attached ESC/POS printer emulator (emulated_printer/), used by
        # its own compose stack to reproduce the PP6800 buffer overflow and
        # validate every print-pacing strategy without the real hardware.
        # Selected with PRINTER_KEY=EMULATED; host/port come from the stack env.
        "vendor": "0x0000",
        "product": "0x0000",
        "name": "Emulated ESC/POS Printer",
        "key": "EMULATED",
        "type": DeviceType.PRINTER,
        "port_type": DevicePortType.NETWORK,
        "conf": {
            "host": os.environ.get("EMULATED_PRINTER_HOST", "emulated_printer"),
            "port": int(os.environ.get("EMULATED_PRINTER_PORT", "9100")),
        },
        "print_width": 512,
        "image_conf": {
            "impl": "bitImageColumn",
            "center": False,
            "high_density_vertical": True,
            "high_density_horizontal": True,
        },
    },
]
