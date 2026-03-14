from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import RunnerConfig, TargetConfig


def _env_lines(prefix: Path, target: TargetConfig, vk_icd: str | None, vulkan_supported: bool) -> list[str]:
    lines = [
        f"WINEPREFIX={prefix}",
        f"WINEARCH={target.wine_arch}",
        "WINEDEBUG=-all",
        "WINEESYNC=1",
        "__GL_THREADED_OPTIMIZATIONS=1",
        "__GL_DISK_CACHE=1",
        f"VK_ICD_FILENAMES={vk_icd or '/usr/share/vulkan/icd.d'}",
        "LATENCYFLEX=1",
    ]
    if vulkan_supported:
        lines.extend(["DXVK_LOG_LEVEL=info", "VKD3D_DEBUG=warn"])
    else:
        lines.append("PROTON_USE_WINED3D=1")
    return lines


def _runner_hint(runner: RunnerConfig) -> str:
    if runner.runner == "proton":
        return f"Proton: {runner.proton_bin}"
    return f"Wine: {runner.wine_bin}"


def _install_cmd(runner: RunnerConfig, installer: str) -> str:
    if runner.runner == "proton":
        return f"{runner.proton_bin} run "{installer}""
    return f"{runner.wine_bin} "{installer}""


def _resolve_exe(prefix: Path) -> str:
    return str(prefix / "drive_c" / "Program Files" / "Blackmagic Design" / "DaVinci Resolve" / "Resolve.exe")


def generate_bottles_docs(
    targets: Iterable[TargetConfig],
    prefix_root: Path,
    output_dir: Path,
    runner: RunnerConfig,
    vk_icd: str | None,
    vulkan_supported: bool,
) -> Path:
    out = output_dir / "bottles-setup.md"
    lines: list[str] = [
        "# Bottles setup for DaVinci Resolve",
        "",
        "These steps create one Bottle per target and apply the same environment we use for Lutris.",
        "",
        f"Runner hint: {_runner_hint(runner)}",
        "",
        "Repeat the steps below for each target you want:",
        "",
    ]
    for target in targets:
        prefix = prefix_root / target.target
        lines.extend(
            [
                f"## {target.display_name}",
                "",
                "1. Create a new Bottle.",
                f"   Name: `{target.target}`",
                "   Type: `gaming` (or `custom`)",
                "2. Set the Bottle to use your Wine/Proton build (if Bottles allows custom runners).",
                "3. Open Bottle environment settings and add these variables:",
                "",
                "```text",
                *[f"{l}" for l in _env_lines(prefix, target, vk_icd, vulkan_supported)],
                "```
",
                "4. Run the Windows installer inside the Bottle.",
                f"   Install command (if using a terminal): `{_install_cmd(runner, 'DaVinci_Resolve_Windows.exe')}`",
                "5. Copy `directml.dll` to `drive_c\windows\system32` inside the Bottle.",
                f"   Prefix path: `{prefix}`",
                "6. Set the program to launch:",
                f"   `{_resolve_exe(prefix)}`",
                "",
            ]
        )

    out.write_text("
".join(lines), encoding="utf-8")
    return out


def generate_heroic_docs(
    targets: Iterable[TargetConfig],
    prefix_root: Path,
    output_dir: Path,
    runner: RunnerConfig,
    vk_icd: str | None,
    vulkan_supported: bool,
) -> Path:
    out = output_dir / "heroic-setup.md"
    lines: list[str] = [
        "# Heroic Games Launcher setup for DaVinci Resolve",
        "",
        "These steps create one Heroic game entry per target and apply the same environment we use for Lutris.",
        "",
        f"Runner hint: {_runner_hint(runner)}",
        "",
        "Repeat the steps below for each target you want:",
        "",
    ]
    for target in targets:
        prefix = prefix_root / target.target
        lines.extend(
            [
                f"## {target.display_name}",
                "",
                "1. Add a game manually in Heroic.",
                f"   Name: `{target.target}`",
                "2. Set a custom Wine/Proton runner if available.",
                "3. Set the Wine prefix to:",
                f"   `{prefix}`",
                "4. Add these environment variables:",
                "",
                "```text",
                *[f"{l}" for l in _env_lines(prefix, target, vk_icd, vulkan_supported)],
                "```
",
                "5. Run the Windows installer with the selected runner.",
                f"   Install command (if using a terminal): `{_install_cmd(runner, 'DaVinci_Resolve_Windows.exe')}`",
                "6. Copy `directml.dll` to `drive_c\windows\system32` inside the prefix.",
                "7. Set the game executable to:",
                f"   `{_resolve_exe(prefix)}`",
                "",
            ]
        )

    out.write_text("
".join(lines), encoding="utf-8")
    return out
