from __future__ import annotations

import logging
import shutil
import subprocess
import sys
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
    # Proton winetricks does not support "dx10"/"dx11" verbs; keep to stable verbs.
    run_cmd([winetricks_bin, "-q", "win10", "vcrun2019"], dep_env, "install-dependencies")


def copy_dlls(
    prefix_root: Path,
    target: TargetConfig,
    runner: RunnerConfig,
    directml: Path,
    opencl: Path | None,
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

    dst_opencl = system32 / "opencl.dll"
    if dst_opencl.exists():
        logging.info("opencl.dll already exists at %s, skipping copy", dst_opencl)
    else:
        source_opencl = opencl
        if source_opencl is None and sys.stdin.isatty():
            user_input = input(
                "opencl.dll not found in prefix. Enter path to opencl.dll (or press Enter to skip): "
            ).strip()
            if user_input:
                source_opencl = Path(user_input).expanduser()

        if source_opencl is None:
            logging.warning("opencl.dll not provided; OpenCL features may not work.")
        elif not source_opencl.exists():
            logging.warning("Provided opencl.dll path does not exist: %s", source_opencl)
        else:
            shutil.copy2(source_opencl, dst_opencl)
            logging.info("Copied opencl.dll to %s", system32)

    if target.arch == "x86_64":
        dst_nvcuda = system32 / "nvcuda.dll"
        if dst_nvcuda.exists():
            logging.info("nvcuda.dll already exists at %s, skipping copy", dst_nvcuda)
            return
        if nvcuda is None:
            logging.warning(
                "nvcuda.dll not found/provided; continuing without CUDA. "
                "Resolve may fall back to non-CUDA GPU paths."
            )
            return
        if not nvcuda.exists():
            logging.warning(
                "nvcuda.dll path was provided but file does not exist: %s. "
                "Continuing without CUDA.",
                nvcuda,
            )
            return
        if gpu_type != "nvidia":
            logging.info("Copying optional nvcuda.dll while gpu-type=%s (experimental)", gpu_type)
        shutil.copy2(nvcuda, dst_nvcuda)
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
        raise RuntimeError(
            f"Unsupported installer format: {installer}. "
            "Use the Windows DaVinci Resolve installer (.exe), not the Linux .run package."
        )
    run_cmd(runner_exec(runner, [str(installer)]), env, "run-installer-exe")
