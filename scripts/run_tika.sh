#!/usr/bin/env bash
set -euo pipefail

if [[ "${LEXNLP_USE_TIKA:-false}" == "true" ]]; then
    SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
    REPOSITORY_ROOT="$(cd -- "${SCRIPT_DIRECTORY}/.." && pwd)"
    port="${APACHE_TIKA_PORT:-9998}"
    binaries="${APACHE_TIKA_BINARIES:-${REPOSITORY_ROOT}/bin}"
    version="${APACHE_TIKA_VERSION:-3.3.2}"
    jar="$binaries/tika-server-standard-$version.jar"

    if [[ ! -f "$jar" ]]; then
        echo "Missing verified Tika server: $jar" >&2
        echo "Run scripts/download_tika.sh first." >&2
        exit 1
    fi

    tika_is_ready() {
        python3 - "$port" "$version" <<'PY'
import http.client
import sys

connection = http.client.HTTPConnection("127.0.0.1", int(sys.argv[1]), timeout=1)
try:
    connection.request("GET", "/version")
    response = connection.getresponse()
    body = response.read(256).decode("utf-8", errors="replace").strip()
finally:
    connection.close()

if response.status != 200 or body != f"Apache Tika {sys.argv[2]}":
    raise SystemExit(1)
PY
    }

    port_is_in_use() {
        python3 - "$port" <<'PY'
import socket
import sys

with socket.socket() as connection:
    connection.settimeout(1)
    raise SystemExit(connection.connect_ex(("127.0.0.1", int(sys.argv[1]))) != 0)
PY
    }

    if tika_is_ready >/dev/null 2>&1; then
        echo "Tika Server $version is already running on 127.0.0.1:$port"
        exit 0
    fi
    if port_is_in_use; then
        echo "Cannot start Tika Server $version: 127.0.0.1:$port is already in use" >&2
        exit 1
    fi

    java -version
    echo "Starting Tika Server $version on 127.0.0.1:$port"
    java -jar "$jar" \
        --host 127.0.0.1 \
        --port "$port" \
        2>"/tmp/tika-server-$version.log" &
fi
