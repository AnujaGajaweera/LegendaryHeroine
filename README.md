# DaVinci Resolve Lutris Installer (Wine/Proton)

Modular automation toolkit for preparing DaVinci Resolve Windows installers on Linux with Wine or Proton, and generating architecture-specific Lutris YAML installers.

## Features

- Supports 4 targets:
  - `davinci-resolve-x86_64`
  - `davinci-resolve-arm64`
  - `davinci-resolve-studio-x86_64`
  - `davinci-resolve-studio-arm64`
- Supports runners:
  - `wine` (custom builds like `resolve-wine`)
  - `proton`
- Uses DXVK + VKD3D + LatencyFleX tuning in generated configs
- Creates per-target prefixes
- Installs dependencies (`win10`, `vcrun2019`)
- Injects DLLs:
  - `directml.dll` (all)
  - `nvcuda.dll` (x86_64 optional, only if needed)
- Applies registry tweaks for DPI and stability
- Runs OpenCL warning check in Lutris installer context (warn-only, does not block install)
- Generates Lutris-ready YAML files
- Logs each step and fails with clear errors

## Project Structure

- `resolve_lutris_installer.py`: Thin entrypoint
- `resolve_installer/`: Python modules
  - `cli.py`: argument parsing and orchestration
  - `runner.py`: runner selection and command wrapping
  - `envcfg.py`: environment and prefix logic
  - `actions.py`: prefix/deps/DLL/registry/install actions
  - `yamlgen.py`: Lutris YAML generator
  - `models.py`: target and runner dataclasses
  - `logging_utils.py`: logger setup
- `tools/prefix_path_check.py`: optional Python helper
- `tools/build_helpers.sh`: checks Python helper
- `buildsystems/`: custom Wine/Proton runtime build systems

## Requirements

- Linux
- Python 3.10+
- `wine` and/or `proton`
- `winetricks`
- DaVinci Resolve Windows installer (`.exe`)
- `directml.dll` (matching architecture)
- `nvcuda.dll` (optional for x86_64)

## Quick Start

### 1. Generate combined YAML (Wine)

```bash
python3 resolve_lutris_installer.py --action generate --runner wine --target all --output-dir .
# writes: davinci-resolve-all.yml
```

### 2. Generate combined YAML (Proton)

```bash
python3 resolve_lutris_installer.py \
  --action generate \
  --runner proton \
  --proton-bin /path/to/proton \
  --target all \
  --output-dir .
# writes: davinci-resolve-all.yml
```

### 3. Install one target + generate YAML

```bash
python3 resolve_lutris_installer.py \
  --action both \
  --runner wine \
  --target davinci-resolve-x86_64 \
  --installer /path/to/Resolve.exe \
  --directml-dll /path/to/directml.dll \
  --gpu-type nvidia
```

### 4. Print Lutris cache path candidates

```bash
python3 resolve_lutris_installer.py --print-lutris-paths
```

## Environment Variables Applied

- `WINEDEBUG=-all`
- `WINEESYNC=1`
- `__GL_THREADED_OPTIMIZATIONS=1`
- `__GL_DISK_CACHE=1`
- `VK_ICD_FILENAMES=/usr/share/vulkan/icd.d`
- `DXVK_LOG_LEVEL=info`
- `VKD3D_DEBUG=warn`
- `LATENCYFLEX=1`

## Check Optional Python Helper

```bash
./tools/build_helpers.sh
./tools/prefix_path_check.py /path/to/prefix
```

## Build Custom Runtimes (resolve-wine / resolve-proton)

```bash
# resolve-wine
./buildsystems/build_runtime.sh --runtime wine --arch x86_64
./buildsystems/build_runtime.sh --runtime wine --arch arm64

# resolve-proton
./buildsystems/build_runtime.sh --runtime proton --arch x86_64
./buildsystems/build_runtime.sh --runtime proton --arch arm64
```

See `buildsystems/README.md` for profiles, patch hooks, and artifact layout.

## Notes

- Targets are intentionally explicit and separate.
- No automatic host architecture switching is performed.
- x86_64 on ARM64 may require external emulation stacks (e.g., box64/FEX).

## License

LGPL-3.0-or-later. See `LICENSE`.
