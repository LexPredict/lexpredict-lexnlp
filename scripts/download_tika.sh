#!/usr/bin/env bash
set -euo pipefail

if [[ "${LEXNLP_USE_TIKA:-false}" == "true" ]]; then
    SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
    REPOSITORY_ROOT="$(cd -- "${SCRIPT_DIRECTORY}/.." && pwd)"
    python3 "${SCRIPT_DIRECTORY}/bootstrap_assets.py" \
        --tika \
        --tika-dir "${APACHE_TIKA_BINARIES:-${REPOSITORY_ROOT}/bin}"
fi
