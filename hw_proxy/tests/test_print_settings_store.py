"""Tests for the JSON-backed persistence of runtime print settings.

These guard the contract that the persisted file is the source of truth (it wins
over env defaults), that runtime edits survive restarts, and that a missing or
corrupt file falls back to the supplied defaults *and* is rewritten so the file
converges to a valid state.
"""

from pathlib import Path

from hw_proxy.core.settings_store import PrintSettingsStore
from hw_proxy.schemas.printer import PrintSettings


def _defaults() -> PrintSettings:
    return PrintSettings(strategy="pace", pace_base_ms=800)


def test_missing_file_seeds_defaults(tmp_path: Path) -> None:
    path = tmp_path / "print_settings.json"
    store = PrintSettingsStore(path, _defaults())

    loaded = store.load()

    assert loaded == _defaults()
    # The defaults are written so the file exists for the next load.
    assert path.exists()
    assert PrintSettings.model_validate_json(path.read_text()) == _defaults()


def test_valid_file_wins_over_defaults(tmp_path: Path) -> None:
    path = tmp_path / "print_settings.json"
    persisted = PrintSettings(strategy="chunked", chunk_size=512)
    path.write_text(persisted.model_dump_json(), encoding="utf-8")
    store = PrintSettingsStore(path, _defaults())

    loaded = store.load()

    assert loaded == persisted
    assert loaded != _defaults()


def test_corrupt_json_falls_back_and_rewrites(tmp_path: Path) -> None:
    path = tmp_path / "print_settings.json"
    path.write_text("{ this is not valid json", encoding="utf-8")
    store = PrintSettingsStore(path, _defaults())

    loaded = store.load()

    assert loaded == _defaults()
    # File is rewritten with valid defaults, so a re-load is now clean.
    assert PrintSettings.model_validate_json(path.read_text()) == _defaults()


def test_out_of_range_values_fall_back_and_rewrite(tmp_path: Path) -> None:
    path = tmp_path / "print_settings.json"
    # chunk_size is bounded to [16, 4096]; 999999 fails validation.
    path.write_text('{"strategy": "chunked", "chunk_size": 999999}', "utf-8")
    store = PrintSettingsStore(path, _defaults())

    loaded = store.load()

    assert loaded == _defaults()
    assert PrintSettings.model_validate_json(path.read_text()) == _defaults()


def test_save_round_trips_and_leaves_no_temp_file(tmp_path: Path) -> None:
    path = tmp_path / "print_settings.json"
    store = PrintSettingsStore(path, _defaults())
    new = PrintSettings(strategy="status_poll", status_poll_timeout_ms=3000)

    store.save(new)

    assert store.load() == new
    assert list(tmp_path.glob("*.tmp")) == []


def test_save_creates_parent_directory(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "dir" / "print_settings.json"
    store = PrintSettingsStore(path, _defaults())

    store.save(_defaults())

    assert path.exists()
