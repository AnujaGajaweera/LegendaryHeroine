#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
  cat <<EOF
Usage: $0 --runtime <wine|proton> --arch <x86_64|arm64> [--jobs N]
EOF
}

RUNTIME=""
ARCH=""
JOBS="$(nproc)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runtime)
      RUNTIME="$2"
      shift 2
      ;;
    --arch)
      ARCH="$2"
      shift 2
      ;;
    --jobs)
      JOBS="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

[[ -n "${RUNTIME}" && -n "${ARCH}" ]] || { usage; exit 1; }

case "${RUNTIME}" in
  wine)
    exec "${SCRIPT_DIR}/wine/build_wine.sh" --arch "${ARCH}" --jobs "${JOBS}"
    ;;
  proton)
    exec "${SCRIPT_DIR}/proton/build_proton.sh" --arch "${ARCH}" --jobs "${JOBS}"
    ;;
  *)
    echo "Invalid runtime: ${RUNTIME}" >&2
    exit 1
    ;;
esac
