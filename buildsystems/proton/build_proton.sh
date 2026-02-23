#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../common.sh
source "${SCRIPT_DIR}/../common.sh"

usage() {
  cat <<EOF
Usage: $0 --arch <x86_64|arm64> [--jobs N]

Builds custom resolve-proton for the selected architecture using Proton sources.
EOF
}

ARCH=""
JOBS="$(nproc)"

while [[ $# -gt 0 ]]; do
  case "$1" in
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
      die "Unknown argument: $1"
      ;;
  esac
done

[[ -n "${ARCH}" ]] || die "--arch is required"
[[ "${ARCH}" == "x86_64" || "${ARCH}" == "arm64" ]] || die "--arch must be x86_64 or arm64"

require_cmd git
require_cmd make
require_cmd tar
require_cmd clang

PROFILE="${SCRIPT_DIR}/config/resolve-proton-${ARCH}.env"
[[ -f "${PROFILE}" ]] || die "Missing profile: ${PROFILE}"
# shellcheck disable=SC1090
source "${PROFILE}"

REPO_DIR="${SRC_DIR}/${OUTPUT_NAME}-src"
WORK_DIR="${BUILD_DIR}/${OUTPUT_NAME}"
INSTALL_DIR="${ARTIFACT_DIR}/${OUTPUT_NAME}"
LOG_FILE="${LOG_DIR}/${OUTPUT_NAME}.log"

exec > >(tee -a "${LOG_FILE}") 2>&1
log "INFO" "Starting ${OUTPUT_NAME} build"
log "INFO" "Host arch: $(host_arch)"

clone_or_update_repo "${PROTON_REPO}" "${REPO_DIR}" "${PROTON_REF}"
apply_patches "${REPO_DIR}" "${SCRIPT_DIR}/patches"

rm -rf "${WORK_DIR}" "${INSTALL_DIR}"
mkdir -p "${WORK_DIR}" "${INSTALL_DIR}"

pushd "${REPO_DIR}" >/dev/null

export CC CXX CFLAGS CXXFLAGS

# Proton ships its own build helpers; we use a non-containerized local build path.
# The exact targets can change across Proton revisions; adjust if your selected ref differs.
if [[ -x ./configure.sh ]]; then
  ./configure.sh --no-steam-runtime
fi

if make help >/dev/null 2>&1; then
  make -j"${JOBS}" redist || make -j"${JOBS}"
else
  make -j"${JOBS}"
fi

# Try common output locations.
if [[ -d ./dist ]]; then
  cp -a ./dist/. "${INSTALL_DIR}/"
elif [[ -d ./redist ]]; then
  cp -a ./redist/. "${INSTALL_DIR}/"
else
  die "No Proton output directory found (expected dist/ or redist/)"
fi

popd >/dev/null

cat > "${INSTALL_DIR}/resolve-proton-build-info.txt" <<EOF
output=${OUTPUT_NAME}
arch=${TARGET_ARCH}
proton_ref=${PROTON_REF}
built_at=$(now_utc)
host_arch=$(host_arch)
EOF

TARBALL="${ARTIFACT_DIR}/${OUTPUT_NAME}.tar.xz"
tar -C "${ARTIFACT_DIR}" -cJf "${TARBALL}" "${OUTPUT_NAME}"

log "INFO" "Build finished: ${TARBALL}"
