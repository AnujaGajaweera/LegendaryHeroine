# Developer Guide: DaVinci Resolve on Linux (LegendaryHeroine)

This document explains architecture, workflow, and design decisions.

## Scope

This toolkit automates:
- Lutris installer YAML generation
- Wine/Proton prefix setup orchestration
- dependency bootstrapping (`win10`, `vcrun2019`)
- DLL staging and registry tweaks for Resolve compatibility

It targets Windows Resolve installers (`.exe`) only.

## Architecture

Main entrypoint:
- `resolve_lutris_installer.py` → delegates to package CLI

Package modules:
- `resolve_installer/cli.py`
  - argument parsing
  - install vs generate orchestration
  - Vulkan support detection handoff
- `resolve_installer/yamlgen.py`
  - builds per-target installer YAML objects
  - emits a single-document YAML list (`davinci-resolve.yml`)
- `resolve_installer/actions.py`
  - prefix creation
  - winetricks dependencies
  - DLL copy logic
  - registry import
  - installer execution
- `resolve_installer/envcfg.py`
  - environment preparation
  - Vulkan capability detection (`vulkaninfo --summary`)
  - DXVK/VKD3D fallback policy
- `resolve_installer/runner.py`
  - Wine/Proton command abstraction
- `resolve_installer/models.py`
  - target metadata
- `resolve_installer/lutris_paths.py`
  - Lutris cache path helpers

## Installer targets

Supported target IDs:
- `davinci-resolve-x86_64`
- `davinci-resolve-arm64`
- `davinci-resolve-studio-x86_64`
- `davinci-resolve-studio-arm64`

Runner options:
- `wine`
- `proton`

## YAML format constraints

Lutris local script loading uses `yaml.safe_load` and expects a single document.
Therefore:
- do **not** emit multi-document YAML (`---`)
- emit one top-level list containing all installers

Output file:
- `davinci-resolve.yml`

## Vulkan / DXVK / VKD3D policy

Runtime behavior:
- If Vulkan detected:
  - `dxvk: true`
  - `vkd3d: true`
  - set DXVK/VKD3D log/debug env vars
- If Vulkan not detected:
  - `dxvk: false`
  - `vkd3d: false`
  - fallback `PROTON_USE_WINED3D=1`

## DLL policy

Required:
- `directml.dll`

Optional:
- `opencl.dll`
  - if missing, installer can prompt user path (install flow)
- `nvcuda.dll` (x86_64 only)
  - optional; warning-only if missing
  - no hard failure

## Installer format policy

Allowed:
- `.exe` only

Rejected:
- `.run` (Linux package, out of scope for Wine/Proton workflow)

## Known compatibility notes

- Older GPUs / incomplete Vulkan stacks may trigger DXVK init errors during some winetricks UI operations.
- Lutris/UMU can inject additional env vars independent of generated YAML.
- Missing i386 graphics libs can degrade Wine runtime behavior:
  - `libGL.so.1` (i386)
  - `libvulkan.so.1` (i386)
  - `libgnutls.so.30` (i386)

## Recommended dev workflow

1. Edit modules.
2. Validate syntax:
   ```bash
   python3 -m py_compile resolve_lutris_installer.py resolve_installer/*.py
