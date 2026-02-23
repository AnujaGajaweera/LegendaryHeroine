from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .actions import apply_registry, copy_dlls, create_prefix, install_dependencies, run_installer
from .envcfg import base_env
from .logging_utils import setup_logging
from .lutris_paths import detect_lutris_cache_dir, lutris_cache_candidates
from .models import TARGETS, TargetConfig
from .runner import select_runner
from .yamlgen import generate_combined_yaml


def install_release(
    cfg: TargetConfig,
    runner,
    installer: Path,
    directml_dll: Path,
    opencl_dll: Path | None,
    nvcuda_dll: Path | None,
    prefix_root: Path,
    winetricks_bin: str,
    gpu_type: str,
    vk_icd: str | None,
) -> None:
    env = base_env(prefix_root, cfg, runner, vk_icd)
    logging.info("Installing %s with runner=%s", cfg.target, runner.runner)
    create_prefix(cfg, prefix_root, runner, env)
    install_dependencies(winetricks_bin, runner, env)
    copy_dlls(prefix_root, cfg, runner, directml_dll, opencl_dll, nvcuda_dll, gpu_type)
    run_installer(installer, runner, env)
    apply_registry(prefix_root, cfg, runner, env)
    logging.info("Install sequence complete for %s", cfg.target)


def generate_yaml_files(targets: list[TargetConfig], prefix_root: Path, output_dir: Path, runner, wine_version: str, proton_version: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / "davinci-resolve.yml"
    out.write_text(
        generate_combined_yaml(targets, prefix_root, runner, wine_version, proton_version),
        encoding="utf-8",
    )
    logging.info("Generated %s", out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DaVinci Resolve modular Wine/Proton installer + Lutris YAML generator")
    parser.add_argument("--action", choices=["install", "generate", "both"], default="both")
    parser.add_argument("--target", choices=["all", *TARGETS.keys()], default="all")
    parser.add_argument("--runner", choices=["wine", "proton"], default="wine")

    parser.add_argument("--installer", type=Path, help="Path to DaVinci Resolve Windows installer (.exe)")
    parser.add_argument("--directml-dll", type=Path, help="Path to directml.dll")
    parser.add_argument("--opencl-dll", type=Path, help="Optional path to opencl.dll")
    parser.add_argument("--nvcuda-dll", type=Path, help="Optional path to nvcuda.dll (x86_64 only)")

    parser.add_argument("--wine-bin", default="wine", help="Wine binary path")
    parser.add_argument("--proton-bin", default=None, help="Proton binary path")
    parser.add_argument("--winetricks-bin", default="winetricks", help="winetricks binary path")

    parser.add_argument("--prefix-root", type=Path, default=Path.home() / "Games")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd())
    parser.add_argument("--wine-version", default="")
    parser.add_argument("--proton-version", default="")
    parser.add_argument("--gpu-type", choices=["nvidia", "amd", "intel", "arm", "unknown"], default="unknown")
    parser.add_argument("--vk-icd", default=None)
    parser.add_argument("--log-file", type=Path, default=Path.cwd() / "resolve-installer.log")
    parser.add_argument("--print-lutris-paths", action="store_true", help="Print detected Lutris cache directories and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.log_file)

    if args.print_lutris_paths:
        for candidate in lutris_cache_candidates():
            status = "exists" if candidate.exists() else "missing"
            print(f"{candidate} [{status}]")
        detected = detect_lutris_cache_dir()
        if detected:
            print(f"detected={detected}")
        else:
            print("detected=<none>")
        return 0

    runner = select_runner(args.runner, args.wine_bin, args.proton_bin)

    targets = list(TARGETS.values()) if args.target == "all" else [TARGETS[args.target]]

    try:
        if args.action in ("install", "both"):
            if args.target == "all":
                raise RuntimeError("Install action requires a single --target (not --target all)")
            if args.installer is None:
                raise RuntimeError("--installer is required for install/both")
            if args.directml_dll is None:
                raise RuntimeError("--directml-dll is required for install/both")

            install_release(
                cfg=targets[0],
                runner=runner,
                installer=args.installer,
                directml_dll=args.directml_dll,
                opencl_dll=args.opencl_dll,
                nvcuda_dll=args.nvcuda_dll,
                prefix_root=args.prefix_root,
                winetricks_bin=args.winetricks_bin,
                gpu_type=args.gpu_type,
                vk_icd=args.vk_icd,
            )

        if args.action in ("generate", "both"):
            generate_yaml_files(targets, args.prefix_root, args.output_dir, runner, args.wine_version, args.proton_version)

    except Exception as exc:
        logging.error("Failure: %s", exc)
        return 1

    logging.info("Completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
