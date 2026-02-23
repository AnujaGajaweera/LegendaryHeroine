# Developer Guide: DaVinci Resolve on Linux (LegendaryHeroine)

This document covers architecture, behavior, and design decisions of the installer toolkit.

## Purpose

Automate DaVinci Resolve Windows installer deployment on Linux through Lutris, with:
- architecture-specific target metadata
- Wine/Proton runner support
- prefix setup + dependency bootstrap
- compatibility DLL copy + registry tweaks
- generation of a single Lutris-local script file (`davinci-resolve.yml`)

## Code Layout

- `resolve_lutris_installer.py`
  - Thin entrypoint to package CLI
- `resolve_installer/cli.py`
  - Top-level orchestration
  - Parses CLI arguments
  - Calls install/generate paths
- `resolve_installer/yamlgen.py`
  - Builds installer objects
  - Emits a single YAML document list (Lutris-compatible)
- `resolve_installer/actions.py`
  - Prefix creation
  - Winetricks dependency step (`win10`, `vcrun2019`)
  - DLL copy logic (`directml`, optional `opencl`, optional `nvcuda`)
  - Registry import
  - Installer execution (Windows `.exe` only)
- `resolve_installer/envcfg.py`
  - Runtime env generation
  - Vulkan detection (`vulkaninfo --summary`)
  - DXVK/VKD3D conditional policy
- `resolve_installer/runner.py`
  - Runner selection and command mapping (`wine` vs `proton`)
- `resolve_installer/models.py`
  - Static target definitions
- `resolve_installer/lutris_paths.py`
  - Lutris cache location helpers

## Lutris Script Format Constraint

Lutris local script loading uses `yaml.safe_load`, not `safe_load_all`.
Therefore the output **must** be:
- one YAML document
- top-level list of installer dictionaries

`yamlgen.generate_combined_yaml()` enforces this.

## Target Matrix

- `davinci-resolve-x86_64`
- `davinci-resolve-arm64`
- `davinci-resolve-studio-x86_64`
- `davinci-resolve-studio-arm64`

## Dependency Policy

Used verbs:
- `win10`
- `vcrun2019`

`dx10`/`dx11` were removed due Proton winetricks compatibility issues.

## DLL Policy

- `directml.dll`: required
- `opencl.dll`: optional
  - if missing, install flow prompts user (TTY)
  - warning-only if unavailable
- `nvcuda.dll`: optional (x86_64 path)
  - copied only when provided and not already present
  - warning-only if missing

## Vulkan / DXVK / VKD3D Policy

Detection:
- `detect_vulkan_support()` calls `vulkaninfo --summary`

If Vulkan is available:
- YAML: `dxvk: true`, `vkd3d: true`
- Env includes `DXVK_LOG_LEVEL`, `VKD3D_DEBUG`

If Vulkan is unavailable:
- YAML: `dxvk: false`, `vkd3d: false`
- Env uses fallback `PROTON_USE_WINED3D=1`

## Installer Input Policy

Accepted installer format:
- `.exe` only

Rejected:
- `.run` (Linux installer package)

## Generation Output

- File: `davinci-resolve.yml`
- Contains all selected targets in one document list

## Development Workflow

1. Edit modules
2. Validate syntax:
   ```bash
   python3 -m py_compile resolve_lutris_installer.py resolve_installer/*.py
   ```
3. Regenerate YAML:
   ```bash
   python3 resolve_lutris_installer.py --action generate --runner wine --target all --output-dir .
   ```
4. Validate top-level YAML shape:
   - list of installers
   - no `---` multi-document separators

## Known Runtime Notes

- Lutris/UMU may inject additional environment variables outside generated YAML.
- Some systems log DXVK initialization noise during winetricks helper UIs.
- Missing i386 graphics libs can still affect Wine runtime behavior and should be installed at OS level.
