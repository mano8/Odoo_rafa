"""File-backed persistence for the runtime-tunable print settings.

The Printer Tuning panel (hw_status UI) edits :class:`PrinterPool`'s live
``PrintSettings`` at runtime via ``POST /system/print_settings``.  Without
persistence those edits live only in memory and are lost on every hw_proxy
restart, reverting to the env defaults.  This store keeps the live values in a
small JSON file so they survive restarts, and makes that file the source of
truth that ``GET /system/print_settings`` (and therefore the hw_status UI)
reflects.

Precedence: a valid JSON file wins over the env defaults.  A missing or corrupt
file falls back to the supplied defaults and is (re)written, so the file always
converges to a valid, consistent state.
"""

import logging
import os
from pathlib import Path

from pydantic import ValidationError

from hw_proxy.schemas.printer import PrintSettings

logger = logging.getLogger("hw_proxy")


class PrintSettingsStore:
    """Load and persist :class:`PrintSettings` as a JSON file."""

    def __init__(self, path: Path, defaults: PrintSettings) -> None:
        self._path = Path(path)
        self._defaults = defaults

    @property
    def path(self) -> Path:
        """Filesystem location of the persisted settings."""
        return self._path

    def load(self) -> PrintSettings:
        """Return the persisted settings, or defaults if missing/corrupt.

        On a missing file the defaults are seeded to disk.  On a corrupt or
        out-of-range file the defaults are used and the file is rewritten so it
        converges to a valid state.
        """
        try:
            raw = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.info(
                "[PrintSettingsStore] no file at %s; seeding from defaults",
                self._path,
            )
            self.save(self._defaults)
            return self._defaults
        except OSError as exc:
            logger.warning(
                "[PrintSettingsStore] cannot read %s (%s); using defaults",
                self._path,
                exc,
            )
            return self._defaults

        try:
            return PrintSettings.model_validate_json(raw)
        except (ValidationError, ValueError) as exc:
            logger.warning(
                "[PrintSettingsStore] corrupt settings file %s (%s); "
                "falling back to defaults and rewriting",
                self._path,
                exc,
            )
            self.save(self._defaults)
            return self._defaults

    def save(self, settings: PrintSettings) -> None:
        """Atomically persist ``settings`` (temp file + ``os.replace``)."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(self._path.suffix + ".tmp")
            tmp.write_text(settings.model_dump_json(indent=2), encoding="utf-8")
            os.replace(tmp, self._path)
        except OSError as exc:
            logger.warning(
                "[PrintSettingsStore] failed to persist %s (%s)",
                self._path,
                exc,
            )
