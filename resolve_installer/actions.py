from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict

from .envcfg import prefix_dir
from .models import RunnerConfig, TargetConfig
from .runner import runner_exec


def run_cmd(cmd: list[str], env: Dict[str, str], step: str) -> None:
    logging.info("[%s] Running: %s", step, " ".join(cmd))
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if result.stdout:
        logging.info("[%s] stdout:\n%s", step, result.stdout.strip())
    if result.stderr:
        logging.info("[%s] stderr:\n%s", step, result.stderr.strip())

    if result.returncode != 0:
        raise RuntimeError(f"Step '{step}' failed with exit code {result.returncode}")


def create_prefix(target: TargetConfig, prefix_root: Path, runner: RunnerConfig, env: Dict[str, str]) -> None:
    (prefix_root / target.target).mkdir(parents=True, exist_ok=True)
    run_cmd(runner_exec(runner, ["wineboot", "-u"]), env, "create-prefix")


def install_dependencies(winetricks_bin: str, runner: RunnerConfig, env: Dict[str, str]) -> None:
    dep_env = env.copy()
    if runner.runner == "proton":
        proton_cmd = f"{runner.proton_bin} run"
        dep_env["WINE"] = proton_cmd
        dep_env["WINE64"] = proton_cmd
    run_cmd([winetricks_bin, "-q", "win10", "vcrun2019", "dx10", "dx11"], dep_env, "install-dependencies")


def copy_dlls(
    prefix_root: Path,
    target: TargetConfig,
    runner: RunnerConfig,
    directml: Path,
    nvcuda: Path | None,
    gpu_type: str,
) -> None:
    system32 = prefix_dir(prefix_root, target, runner) / "drive_c" / "windows" / "system32"
    if not system32.exists():
        raise RuntimeError(f"system32 directory not found: {system32}")
    if not directml.exists():
        raise RuntimeError(f"directml.dll not found: {directml}")

    shutil.copy2(directml, system32 / "directml.dll")
    logging.info("Copied directml.dll to %s", system32)

    if target.arch == "x86_64":
        if gpu_type != "nvidia":
            logging.info("x86_64 target selected; nvcuda.dll is optional experimental (gpu-type=%s)", gpu_type)
        if nvcuda is None:
            raise RuntimeError("x86_64 target requires --nvcuda-dll per requested workflow")
        if not nvcuda.exists():
            raise RuntimeError(f"nvcuda.dll not found: {nvcuda}")
        shutil.copy2(nvcuda, system32 / "nvcuda.dll")
        logging.info("Copied nvcuda.dll to %s", system32)


def apply_registry(prefix_root: Path, target: TargetConfig, runner: RunnerConfig, env: Dict[str, str]) -> None:
    target_prefix = prefix_dir(prefix_root, target, runner)
    reg_file = target_prefix / "resolve-tweaks.reg"
    include_cuda = target.arch == "x86_64"

    lines = [
        "REGEDIT4",
        "",
        "[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]",
        '"directml"="native,builtin"',
    ]
    if include_cuda:
        lines.append('"nvcuda"="native,builtin"')

    lines.extend(
        [
            "",
            "[HKEY_CURRENT_USER\\Software\\Wine\\Direct3D]",
            '"renderer"="vulkan"',
            '"csmt"="enabled"',
            '"VideoMemorySize"="0"',
            "",
            "[HKEY_CURRENT_USER\\Control Panel\\Desktop]",
            '"LogPixels"=dword:00000060',
            "",
            "[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers]",
            '"C:\\\\Program Files\\\\Blackmagic Design\\\\DaVinci Resolve\\\\Resolve.exe"="~ HIGHDPIAWARE DISABLEDXMAXIMIZEDWINDOWEDMODE"',
            "",
            "[HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile]",
            '"SystemResponsiveness"=dword:0000000a',
            "",
        ]
    )
    reg_file.write_text("\n".join(lines), encoding="utf-8")
    run_cmd(runner_exec(runner, ["regedit", "/S", str(reg_file)]), env, "apply-registry")


def run_installer(installer: Path, runner: RunnerConfig, env: Dict[str, str]) -> None:
    if not installer.exists():
        raise RuntimeError(f"Installer not found: {installer}")
    if installer.suffix.lower() == ".run":
        run_cmd(["bash", str(installer)], env, "run-installer-run")
    else:
        run_cmd(runner_exec(runner, [str(installer)]), env, "run-installer-exe")
