from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class TargetConfig:
    target: str
    release: str
    arch: str
    display_name: str

    @property
    def wine_arch(self) -> str:
        return "win64" if self.arch == "x86_64" else "arm64"


@dataclass(frozen=True)
class RunnerConfig:
    runner: str
    wine_bin: str
    proton_bin: str | None


TARGETS: Dict[str, TargetConfig] = {
    "davinci-resolve-x86_64": TargetConfig(
        target="davinci-resolve-x86_64",
        release="davinci-resolve",
        arch="x86_64",
        display_name="DaVinci Resolve Free (x86_64)",
    ),
    "davinci-resolve-arm64": TargetConfig(
        target="davinci-resolve-arm64",
        release="davinci-resolve",
        arch="ARM64",
        display_name="DaVinci Resolve Free (ARM64)",
    ),
    "davinci-resolve-studio-x86_64": TargetConfig(
        target="davinci-resolve-studio-x86_64",
        release="davinci-resolve-studio",
        arch="x86_64",
        display_name="DaVinci Resolve Studio (x86_64)",
    ),
    "davinci-resolve-studio-arm64": TargetConfig(
        target="davinci-resolve-studio-arm64",
        release="davinci-resolve-studio",
        arch="ARM64",
        display_name="DaVinci Resolve Studio (ARM64)",
    ),
}
