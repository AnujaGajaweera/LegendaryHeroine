#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../common.sh
source "${SCRIPT_DIR}/../common.sh"

usage() {
  cat <<EOF
Usage: $0 --arch <x86_64|arm64> [--jobs N]

Builds custom resolve-wine for the selected architecture.
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
require_cmd lld

PROFILE="${SCRIPT_DIR}/config/resolve-wine-${ARCH}.env"
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

clone_or_update_repo "${WINE_REPO}" "${REPO_DIR}" "${WINE_REF}"
apply_patches "${REPO_DIR}" "${SCRIPT_DIR}/patches"

rm -rf "${WORK_DIR}" "${INSTALL_DIR}"
mkdir -p "${WORK_DIR}" "${INSTALL_DIR}"

pushd "${WORK_DIR}" >/dev/null

export CC CXX LD CFLAGS CXXFLAGS LDFLAGS

"${REPO_DIR}/configure" --prefix="${INSTALL_DIR}" ${CONFIGURE_FLAGS}
make -j"${JOBS}"
make install

popd >/dev/null

cat > "${INSTALL_DIR}/resolve-wine-build-info.txt" <<EOF
output=${OUTPUT_NAME}
arch=${TARGET_ARCH}
wine_ref=${WINE_REF}
built_at=$(now_utc)
host_arch=$(host_arch)
EOF

TARBALL="${ARTIFACT_DIR}/${OUTPUT_NAME}.tar.xz"
tar -C "${ARTIFACT_DIR}" -cJf "${TARBALL}" "${OUTPUT_NAME}"

log "INFO" "Build finished: ${TARBALL}"
