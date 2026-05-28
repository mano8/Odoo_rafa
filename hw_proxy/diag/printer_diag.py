#!/usr/bin/env python3
"""
PP6800 live printer diagnostic.

Sends 3 labelled text jobs in sequence over the serial port so you can
verify on paper that:
  - each job prints exactly once
  - jobs are in the correct order (JOB 1, JOB 2, JOB 3)
  - no content from a previous job bleeds into the next one

Usage (on the server, stop hw_proxy first to release the port):
    sudo /opt/hw_proxy/.venv/bin/python3 /opt/hw_proxy/diag/printer_diag.py

Optional args:
    --dev  /dev/ttyACM0    serial device  (default: /dev/ttyACM0)
    --baud 115200          baud rate      (default: 115200)
"""

import argparse
import sys
import time

sys.path.insert(0, "/opt/hw_proxy/.venv/lib/python3.12/site-packages")

import serial
from escpos.printer import Dummy

W = 42  # characters per line (PP6800 font A)

CMD_INIT = b"\x1b\x40"
CMD_PRE_PRINT = b"\x1d\x28\x45\x05\x00\x01\x01\x14"
CMD_CP858 = b"\x1b\x74\x13"


def make_payload(lines: list[str]) -> bytes:
    d = Dummy()
    d._raw(CMD_CP858)
    for line in lines:
        d.set(align="center", bold=False, width=1, height=1)
        d._raw((line[:W] + "\n").encode("cp858", errors="replace"))
    d.cut(feed=True)
    return CMD_INIT + CMD_PRE_PRINT + d.output


def send(ser: serial.Serial, payload: bytes, label: str, baud: int) -> None:
    print(f"  -> {label}  ({len(payload)} bytes)")
    ser.write(payload)
    ser.flush()
    wait = len(payload) * 10 / baud
    print(f"     uart drain: {wait:.3f}s ...")
    time.sleep(wait)
    print("     done.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="PP6800 printer diagnostic")
    parser.add_argument("--dev", default="/dev/ttyACM0")
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args()

    print(f"Opening {args.dev} @ {args.baud} baud")
    ser = serial.Serial(
        args.dev,
        args.baud,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=2,
        dsrdtr=False,
    )
    time.sleep(0.3)
    print("Port open.\n")

    jobs = [
        (
            "JOB 1",
            [
                "=" * W,
                "*** JOB 1 - HEADER ***",
                "-" * W,
                "body line A",
                "body line B",
                "body line C",
                "-" * W,
                "*** JOB 1 - FOOTER ***",
                "=" * W,
            ],
        ),
        (
            "JOB 2",
            [
                "=" * W,
                "*** JOB 2 - HEADER ***",
                "-" * W,
                "body line A",
                "body line B",
                "-" * W,
                "*** JOB 2 - FOOTER ***",
                "=" * W,
            ],
        ),
        (
            "JOB 3",
            [
                "=" * W,
                "*** JOB 3 - HEADER ***",
                "-" * W,
                "single body line",
                "-" * W,
                "*** JOB 3 - FOOTER ***",
                "=" * W,
            ],
        ),
    ]

    for label, lines in jobs:
        print(f"=== {label} ===")
        send(ser, make_payload(lines), label, args.baud)

    ser.close()
    print("All done.")
    print("Expected paper: 3 clean receipts in order, no bleed between jobs.")


if __name__ == "__main__":
    main()
