#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OLD_ROOT="${1:-/Users/gaofeng/workspace/Archive/数字分身}"
STATE_DIR="${CODEX_MAIL_HOME:-${HOME}/.codex-mail-workbench}"

mkdir -p "${STATE_DIR}"

install -m 600 "${ROOT_DIR}/config/accounts.example.yaml" "${STATE_DIR}/accounts.yaml"

if [[ -f "${OLD_ROOT}/operations/email/store/email_raw_v1.sqlite" ]]; then
  install -m 600 "${OLD_ROOT}/operations/email/store/email_raw_v1.sqlite" "${STATE_DIR}/mail.sqlite"
  for suffix in -wal -shm; do
    if [[ -f "${OLD_ROOT}/operations/email/store/email_raw_v1.sqlite${suffix}" ]]; then
      install -m 600 "${OLD_ROOT}/operations/email/store/email_raw_v1.sqlite${suffix}" "${STATE_DIR}/mail.sqlite${suffix}"
    fi
  done
fi

if [[ -d "${OLD_ROOT}/operations/email/sync-state" ]]; then
  mkdir -p "${STATE_DIR}/sync-state"
  cp -p "${OLD_ROOT}"/operations/email/sync-state/*.json "${STATE_DIR}/sync-state/" 2>/dev/null || true
fi

echo "[OK] migrated mail config/store to ${STATE_DIR}"

