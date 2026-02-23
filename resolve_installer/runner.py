from __future__ import annotations

from pathlib import Path

from .models import RunnerConfig


def select_runner(runner: str, wine_bin: str, proton_bin: str | None) -> RunnerConfig:
    if runner == "wine":
        return RunnerConfig(runner="wine", wine_bin=wine_bin, proton_bin=None)
    if runner == "proton":
        if not proton_bin:
            raise RuntimeError("--proton-bin is required when --runner proton")
        if not Path(proton_bin).exists():
            raise RuntimeError(f"Proton binary not found: {proton_bin}")
        return RunnerConfig(runner="proton", wine_bin=wine_bin, proton_bin=proton_bin)
    raise RuntimeError(f"Unsupported runner: {runner}")


def runner_exec(cfg: RunnerConfig, args: list[str]) -> list[str]:
    if cfg.runner == "wine":
        return [cfg.wine_bin, *args]
    return [cfg.proton_bin, "run", *args]  # type: ignore[list-item]
