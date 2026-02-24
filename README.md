# DaVinci Resolve on Linux (Easy Installer)

This project helps you install **DaVinci Resolve (Windows version)** on Linux using **Lutris + Wine/Proton**.

It is designed for normal users:
- fewer manual steps
- clear warnings instead of cryptic failures
- one installer YAML file for Lutris import

## What this project does

- Creates installer configs for:
  - Resolve Free (x86_64)
  - Resolve Free (ARM64)
  - Resolve Studio (x86_64)
  - Resolve Studio (ARM64)
- Generates one file: `davinci-resolve.yml`
- Installs common runtime dependencies
- Applies compatibility tweaks
- Handles optional GPU DLLs safely

## Before you start

You need:
- Linux desktop
- Lutris installed
- Wine and/or Proton available in Lutris
- `winetricks`
- DaVinci Resolve **Windows installer** (`.exe`)
- `directml.dll` (required)

Optional:
- `opencl.dll` (you can be prompted if missing)
- `nvcuda.dll` (optional for NVIDIA/CUDA on x86_64)

## Quick start (simple)

1. Generate the Lutris installer file:
   ```bash
   python3 resolve_lutris_installer.py --action generate --runner wine --target all --output-dir .
