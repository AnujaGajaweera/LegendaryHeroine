from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from .models import RunnerConfig, TargetConfig


def prefix_dir(prefix_root: Path, target: TargetConfig, runner: RunnerConfig) -> Path:
    base = prefix_root / target.target
    return base / "pfx" if runner.runner == "proton" else base


def base_env(
    prefix_root: Path,
    target: TargetConfig,
    runner: RunnerConfig,
    vk_icd: str | None,
) -> Dict[str, str]:
    target_prefix = prefix_root / target.target
    env = os.environ.copy()
    env["WINEPREFIX"] = str(prefix_dir(prefix_root, target, runner))
    env["WINEARCH"] = target.wine_arch
    env["WINEDEBUG"] = "-all"
    env["WINEESYNC"] = "1"
    env["__GL_THREADED_OPTIMIZATIONS"] = "1"
    env["__GL_DISK_CACHE"] = "1"
    env["VK_ICD_FILENAMES"] = vk_icd if vk_icd else "/usr/share/vulkan/icd.d"
    env["DXVK_LOG_LEVEL"] = "info"
    env["VKD3D_DEBUG"] = "warn"
    env["LATENCYFLEX"] = "1"
    if runner.runner == "proton":
        env["STEAM_COMPAT_DATA_PATH"] = str(target_prefix)
    return env
