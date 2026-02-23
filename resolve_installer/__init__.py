"""resolve_installer package."""

from .lutris_paths import detect_lutris_cache_dir, lutris_cache_candidates
from .models import RunnerConfig, TARGETS, TargetConfig

__all__ = [
    "RunnerConfig",
    "TargetConfig",
    "TARGETS",
    "detect_lutris_cache_dir",
    "lutris_cache_candidates",
]

__version__ = "0.1.0"
