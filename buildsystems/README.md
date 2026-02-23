# Runtime Build Systems

This directory contains reproducible build systems for custom:
- `resolve-wine`
- `resolve-proton`

## Layout

- `common.sh`: shared utilities
- `build_runtime.sh`: unified entrypoint
- `wine/`: wine build system
- `proton/`: proton build system
- `logs/`: build logs
- `sources/`: git clones
- `build/`: intermediate build directories
- `artifacts/`: install trees + packaged tarballs

## Build resolve-wine

```bash
./buildsystems/build_runtime.sh --runtime wine --arch x86_64
./buildsystems/build_runtime.sh --runtime wine --arch arm64
```

## Build resolve-proton

```bash
./buildsystems/build_runtime.sh --runtime proton --arch x86_64
./buildsystems/build_runtime.sh --runtime proton --arch arm64
```

## Artifacts

Artifacts are emitted to:
- `buildsystems/artifacts/resolve-wine-<arch>/`
- `buildsystems/artifacts/resolve-proton-<arch>/`
- `buildsystems/artifacts/*.tar.xz`

## Notes

- These scripts use local/native builds and are designed for debugability.
- Proton build targets can differ by tag; if a specific `PROTON_REF` changes target names, adjust `proton/build_proton.sh` accordingly.
- Add patches under `wine/patches/` and `proton/patches/`.
