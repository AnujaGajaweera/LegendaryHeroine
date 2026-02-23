from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict

from .models import RunnerConfig, TargetConfig


def prefix_dir(prefix_root: Path, target: TargetConfig, runner: RunnerConfig) -> Path:
    base = prefix_root / target.target
    return base / "pfx" if runner.runner == "proton" else base


def _parse_vulkan_version(text: str) -> tuple[int, int, int] | None:
    for raw in text.splitlines():
        line = raw.strip().lower()
        if "api version" not in line:
            continue
        parts = raw.replace(",", " ").split()
        for token in parts:
            token = token.strip()
            if token.count(".") >= 2 and token[0].isdigit():
                try:
                    major, minor, patch = token.split(".")[:3]
                    return (int(major), int(minor), int(patch))
                except ValueError:
                    continue
    return None


def detect_vulkan_support(min_api: tuple[int, int, int] = (1, 3, 0)) -> bool:
    """Return True only when Vulkan is available and API version is high enough for DXVK/VKD3D."""
    vulkaninfo = shutil.which("vulkaninfo")
    if not vulkaninfo:
        return False

    for args in ([vulkaninfo, "--summary"], [vulkaninfo]):
        try:
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue

        if result.returncode != 0 or not result.stdout:
            continue

        version = _parse_vulkan_version(result.stdout)
        if version is None:
            continue
        return version >= min_api

    return False


def base_env(
    prefix_root: Path,
    target: TargetConfig,
    runner: RunnerConfig,
    vk_icd: str | None,
    vulkan_supported: bool,
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
    if vulkan_supported:
        env["DXVK_LOG_LEVEL"] = "info"
        env["VKD3D_DEBUG"] = "warn"
    else:
        # Fallback path when Vulkan is unavailable.
        env["PROTON_USE_WINED3D"] = "1"
    env["LATENCYFLEX"] = "1"
    if runner.runner == "proton":
        env["STEAM_COMPAT_DATA_PATH"] = str(target_prefix)
    return env
