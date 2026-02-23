#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_ROOT="${ROOT_DIR}/buildsystems"
LOG_DIR="${BUILD_ROOT}/logs"
SRC_DIR="${BUILD_ROOT}/sources"
BUILD_DIR="${BUILD_ROOT}/build"
ARTIFACT_DIR="${BUILD_ROOT}/artifacts"

mkdir -p "${LOG_DIR}" "${SRC_DIR}" "${BUILD_DIR}" "${ARTIFACT_DIR}"

now_utc() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

log() {
  local level="$1"
  shift
  printf "%s [%s] %s\n" "$(now_utc)" "${level}" "$*"
}

die() {
  log "ERROR" "$*"
  exit 1
}

require_cmd() {
  local cmd="$1"
  command -v "${cmd}" >/dev/null 2>&1 || die "Required command missing: ${cmd}"
}

clone_or_update_repo() {
  local repo_url="$1"
  local repo_dir="$2"
  local git_ref="$3"

  if [[ ! -d "${repo_dir}/.git" ]]; then
    log "INFO" "Cloning ${repo_url} into ${repo_dir}"
    git clone --recursive "${repo_url}" "${repo_dir}"
  fi

  log "INFO" "Updating ${repo_dir} to ${git_ref}"
  git -C "${repo_dir}" fetch --tags --prune origin
  git -C "${repo_dir}" checkout "${git_ref}"
  git -C "${repo_dir}" submodule update --init --recursive
}

apply_patches() {
  local src_dir="$1"
  local patch_dir="$2"

  shopt -s nullglob
  local patches=("${patch_dir}"/*.patch)
  shopt -u nullglob

  if [[ ${#patches[@]} -eq 0 ]]; then
    log "INFO" "No patches found in ${patch_dir}; skipping"
    return
  fi

  for patch in "${patches[@]}"; do
    log "INFO" "Applying patch ${patch}"
    git -C "${src_dir}" apply --check "${patch}"
    git -C "${src_dir}" apply "${patch}"
  done
}

host_arch() {
  uname -m
}
