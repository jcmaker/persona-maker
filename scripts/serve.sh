#!/usr/bin/env bash
# persona-maker visualization local-server launcher.
# Usage: serve.sh [personas-dir]   (default: ./personas)
#
# 1) Reuse an existing server in 8765-8775 that is already serving index.html
# 2) Otherwise find a free port and start python3 http.server in the background
# Output: the access URL on one line (stdout). Exits 1 on failure.
set -euo pipefail

DIR="${1:-personas}"
PORT_START=8765
PORT_END=8775

if [[ ! -f "$DIR/index.html" ]]; then
  echo "error: $DIR/index.html not found. Build the visualization with build.py first." >&2
  exit 1
fi

probe() { # $1=port → returns 0 if already serving
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 1 "http://localhost:$1/index.html" || true)
  [[ "$code" == "200" ]]
}

# 1) Reuse an existing server
for ((port=PORT_START; port<=PORT_END; port++)); do
  if probe "$port"; then
    echo "http://localhost:$port/index.html"
    exit 0
  fi
done

# 2) Start a new server
for ((port=PORT_START; port<=PORT_END; port++)); do
  if python3 -m http.server "$port" --directory "$DIR" >/dev/null 2>&1 &
  then
    server_pid=$!
    sleep 1
    if probe "$port"; then
      echo "http://localhost:$port/index.html"
      exit 0
    fi
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi
done

echo "error: tried ports $PORT_START-$PORT_END but could not open a server." >&2
echo "run manually: python3 -m http.server <port> --directory $DIR" >&2
exit 1
