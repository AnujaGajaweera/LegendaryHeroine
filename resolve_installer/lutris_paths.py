from __future__ import annotations

from pathlib import Path


def lutris_cache_candidates() -> list[Path]:
    """Return common Lutris cache locations (native + Flatpak)."""
    home = Path.home()
    return [
        home / ".cache" / "lutris",
        home / ".var" / "app" / "net.lutris.Lutris" / "cache" / "lutris",
    ]


def detect_lutris_cache_dir() -> Path | None:
    """Return the first existing Lutris cache directory, if any."""
    for candidate in lutris_cache_candidates():
        if candidate.exists():
            return candidate
    return None
