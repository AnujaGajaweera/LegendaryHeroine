# DaVinci Resolve on Linux (Easy Guide)

This project helps you install **DaVinci Resolve (Windows version)** on Linux using **Lutris + Wine/Proton**.

It is designed for non-technical users:
- fewer manual steps
- clear warnings instead of cryptic failures
- one installer YAML file for Lutris import

## What You Get

- Support for 4 DaVinci targets:
  - `davinci-resolve-x86_64`
  - `davinci-resolve-arm64`
  - `davinci-resolve-studio-x86_64`
  - `davinci-resolve-studio-arm64`
- One output installer file: `davinci-resolve.yml`
- Works with both `wine` and `proton` runners
- Auto fallback if Vulkan is not supported (DXVK/VKD3D disabled automatically)

## What You Need

Required:
- Linux desktop
- Lutris
- Wine and/or Proton in Lutris
- `winetricks`
- DaVinci Resolve **Windows** installer (`.exe`)
- `directml.dll` (required)

Optional:
- `opencl.dll` (you can provide it when prompted)
- `nvcuda.dll` (optional for NVIDIA/CUDA on x86_64)

## Quick Start

### 1. Generate installer file

```bash
python3 resolve_lutris_installer.py --action generate --runner wine --target all --output-dir .
```

This creates:
- `davinci-resolve.yml`

### 2. Import in Lutris

1. Open Lutris
2. Click `+`
3. Choose `Install from a local install script`
4. Select `davinci-resolve.yml`
5. Pick the Resolve variant you want

### 3. Follow prompts

- Select Resolve `.exe` installer when asked
- Select `directml.dll`
- If `opencl.dll` is missing, the script can ask for a path
- `nvcuda.dll` is optional; if missing, installation continues with warning

## Useful Commands

Generate using Proton profile:
```bash
python3 resolve_lutris_installer.py \
  --action generate \
  --runner proton \
  --proton-bin /path/to/proton \
  --target all \
  --output-dir .
```

Show Lutris cache path candidates:
```bash
python3 resolve_lutris_installer.py --print-lutris-paths
```

## If Something Fails

- `.run` installer is not supported (use `.exe` only)
- If Vulkan is unavailable, DXVK/VKD3D are automatically disabled
- If optional DLLs are missing, you will get warnings, not hard failure

## For Developers

Technical details are documented in `DEVELOPER.md`.

## License

LGPL-3.0-or-later. See `LICENSE`.
