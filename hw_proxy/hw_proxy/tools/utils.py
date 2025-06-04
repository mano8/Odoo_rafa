"""
Hw_proxy utils
"""
import logging
import os
from os.path import join as Pjoin
import termios
import subprocess
from datetime import datetime, timedelta
from typing import List
from dateutil.parser import parse as dateparse
from hw_proxy.core.exceptions import HwHardwareError
from hw_proxy.tools.pos_helper import EscPosHelper
from hw_proxy.core.config import settings

logger = logging.getLogger("hw_proxy")

BASH_SCRIPT_PATH = "/opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/"
# A mapping from termios speed constants → integer baud rates
_BAUD_MAP = {
    termios.B0:       0,
    termios.B50:     50,
    termios.B75:     75,
    termios.B110:   110,
    termios.B134:   134,
    termios.B150:   150,
    termios.B200:   200,
    termios.B300:   300,
    termios.B600:   600,
    termios.B1200: 1200,
    termios.B1800: 1800,
    termios.B2400: 2400,
    termios.B4800: 4800,
    termios.B9600: 9600,
    termios.B19200: 19200,
    termios.B38400: 38400,
    termios.B57600: 57600,
    termios.B115200: 115200,
    termios.B230400: 230400,
    termios.B460800: 460800,
    termios.B500000: 500000,
    termios.B576000: 576000,
    termios.B921600: 921600,
    termios.B1000000: 1000000,
    termios.B1152000: 1152000,
    termios.B1500000: 1500000,
    termios.B2000000: 2000000,
    termios.B2500000: 2500000,
    termios.B3000000: 3000000,
    termios.B3500000: 3500000,
    termios.B4000000: 4000000,
}


class HwUtils:
    """Hw_proxy utils"""
    @staticmethod
    def run_bash_script(
        script: str,
        args: List[str] = None,
        with_sudo: bool = True
    ):
        """Run bash script"""
        script_path = Pjoin(BASH_SCRIPT_PATH, script)
        if with_sudo is True:
            cmd = ["/usr/bin/sudo", script_path]
        else:
            cmd = [script_path]
        if args:
            cmd += args
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(
                "[run_bash_script] An error ocurrent on run "
                f"subprocess, error: {result.stderr.strip()}"
            )
            raise RuntimeError(f"Error: {result.stderr.strip()}")

        return result.stdout.strip()

    @staticmethod
    def parse_relative_time(s: str):
        """
        Parse strings like "5min", "10m", or ISO timestamps into datetime.
        Returns a datetime object or None.
        """
        s = s.strip().lower()
        now = datetime.now()
        try:
            if s.endswith("min") or s.endswith("m"):
                minutes = int(''.join(filter(str.isdigit, s)))
                return now - timedelta(minutes=minutes)
            else:
                # try to parse ISO date
                return dateparse(s)
        except Exception as e:
            logger.error(
                "[parse_relative_time] Unable to parse relative time "
                f"error: {str(e)}"
            )
            return None

    @staticmethod
    def get_serial_config(devfile: str) -> dict:
        """
        Returns the *actual* current serial-line settings
        (baudrate, bytesize, parity, stopbits)
        for the given device path (e.g. "/dev/ttyACM0"),
        by calling termios.tcgetattr().
        """
        try:
            # Open the port read‐only (no controlling terminal),
            # so we only *read* settings
            fd = os.open(devfile, os.O_RDONLY | os.O_NOCTTY)
            try:
                attrs = termios.tcgetattr(fd)
            finally:
                os.close(fd)

            # attrs is a list: [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
            cflag = attrs[2]
            ispeed = attrs[4]

            # Map termios‐constant baud → integer
            baudrate = _BAUD_MAP.get(ispeed, None)

            # Data‐bits mask (CSIZE bits)
            size_flag = cflag & termios.CSIZE
            bytesize = {
                termios.CS5: 5,
                termios.CS6: 6,
                termios.CS7: 7,
                termios.CS8: 8,
            }.get(size_flag, None)

            # Parity: if PARENB set then check PARODD; otherwise 'N'
            if cflag & termios.PARENB:
                parity = 'O' if (cflag & termios.PARODD) else 'E'
            else:
                parity = 'N'

            # Stopbits: if CSTOPB set, that means 2 stop bits; else 1
            stopbits = 2 if (cflag & termios.CSTOPB) else 1

            return {
                "devfile": devfile,
                "baudrate": baudrate,
                "bytesize": bytesize,
                "parity": parity,
                "stopbits": stopbits,
            }
        except Exception as e:
            raise HwHardwareError(
                "[get_serial_config] Fatal Error: "
                "Unable to get current serial configuration "
                f"for device: {devfile} - "
                f"error: {e}"
            ) from e

    @staticmethod
    def get_printer_conection_status() -> dict:
        """Get posiflex connexion status"""
        result = None
        try:
            result = subprocess.run(
                ["/usr/bin/lsusb"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                result = {
                    "status": "error",
                    "message": "Failed to run lsusb"
                }
            output = result.stdout.lower()
            if "0d3a:0368" in output:
                result = {
                    "status": "connected",
                    "message": "Posiflex PP6800 detected on the system."
                }
            else:
                result = {
                    "status": "disconnected",
                    "message": "Posiflex PP6800 not found."
                }
        except Exception as e:
            raise HwHardwareError(
                "[get_posiflex_status] Fatal Error: "
                "Unable to get current posiflex conexion status "
                f"error: {e}"
            ) from e
        return result

    @staticmethod
    def get_printer_global_status() -> dict:
        """Get posiflex connexion status"""
        result = None
        try:
            pos = EscPosHelper(settings.PRINTER_KEY)
            status = pos.get_full_printer_status()
            conection = HwUtils.get_printer_conection_status()
            serial_config = HwUtils.get_serial_config(pos.device.conf.devfile)

            result = {
                "devicePortType": 'SERIAL'
            }
            if isinstance(status, dict):
                result.update({
                    "printerOnline": status.get('is_online'),
                    "paperOk": status.get('paper_status') == "ok",
                    "paperLow": status.get('paper_status') == "near_end",
                })

            if isinstance(conection, dict):
                result.update({
                    "connected": conection.get('status') == "connected",
                })

            if isinstance(serial_config, dict):
                serial_config.update({
                    "readStatus": True,
                    "writeStatus": True,
                })
                result.update({
                    "serialInfo": serial_config
                })

            return result
        except Exception as e:
            raise HwHardwareError(
                "[get_posiflex_status] Fatal Error: "
                "Unable to get current posiflex conexion status "
                f"error: {e}"
            ) from e

    @staticmethod
    def print_dummy_ticket() -> dict:
        """Print dummy ticket for test"""
        try:
            pos = EscPosHelper(settings.PRINTER_KEY)
            pos.print_dummy_receipt()
            return {"success": True}
        except Exception as e:
            raise HwHardwareError(
                "[get_posiflex_status] Fatal Error: "
                "Unable to get current posiflex conexion status "
                f"error: {e}"
            ) from e

    @staticmethod
    def open_cash_drawer() -> dict:
        """Test open cash drawer"""
        try:
            pos = EscPosHelper(settings.PRINTER_KEY)
            pos.open_cashdrawer()
            return {"success": True}
        except Exception as e:
            raise HwHardwareError(
                "[get_posiflex_status] Fatal Error: "
                "Unable to get current posiflex conexion status "
                f"error: {e}"
            ) from e
