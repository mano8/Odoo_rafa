"""Put the emulator package on sys.path so ``import emulator`` resolves."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
