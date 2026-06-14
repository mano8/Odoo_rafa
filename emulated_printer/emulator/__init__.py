"""Controllable ESC/POS printer emulator.

A small, transport-agnostic state machine (:mod:`emulator.core`) that models a
receipt printer's finite input buffer and head print speed, plus two transport
adapters (:mod:`emulator.tcp_server`, :mod:`emulator.pty_server`) that expose it
over TCP or a socat PTY pair.  It reproduces the PP6800 buffer-overflow failure
so the hw_proxy print-pacing strategies can be validated without the hardware.
"""

from emulator.core import PrinterEmulator

__all__ = ["PrinterEmulator"]
