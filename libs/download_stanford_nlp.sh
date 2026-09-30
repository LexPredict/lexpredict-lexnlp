#!/usr/bin/env bash
set -euo pipefail

if [[ "${LEXNLP_USE_STANFORD:-false}" == "true" ]]; then
    SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
    REPOSITORY_ROOT="$(cd -- "${SCRIPT_DIRECTORY}/.." && pwd)"
    stanford_arguments=(--stanford)
    if [[ -n "${STANFORD_NLP_PATH:-}" ]]; then
        stanford_arguments+=(--stanford-dir "${STANFORD_NLP_PATH}")
    fi
    python3 "${REPOSITORY_ROOT}/scripts/bootstrap_assets.py" "${stanford_arguments[@]}"
fi
