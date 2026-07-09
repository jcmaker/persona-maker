#!/usr/bin/env bash
# persona-maker 시각화 로컬 서버 기동 스크립트.
# 사용법: serve.sh [personas-dir]   (기본: ./personas)
#
# 1) 8765~8775 중 이미 index.html을 서빙 중인 서버가 있으면 재사용
# 2) 없으면 빈 포트를 찾아 python3 http.server를 백그라운드로 기동
# 출력: 접속 URL 한 줄 (stdout). 실패 시 exit 1.
set -euo pipefail

DIR="${1:-personas}"
PORT_START=8765
PORT_END=8775

if [[ ! -f "$DIR/index.html" ]]; then
  echo "오류: $DIR/index.html이 없습니다. 먼저 build.py로 시각화를 빌드하세요." >&2
  exit 1
fi

probe() { # $1=port → 이미 서빙 중이면 0
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 1 "http://localhost:$1/index.html" || true)
  [[ "$code" == "200" ]]
}

# 1) 기존 서버 재사용
for ((port=PORT_START; port<=PORT_END; port++)); do
  if probe "$port"; then
    echo "http://localhost:$port/index.html"
    exit 0
  fi
done

# 2) 새 서버 기동
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

echo "오류: $PORT_START~$PORT_END 포트를 모두 시도했지만 서버를 열지 못했습니다." >&2
echo "직접 실행: python3 -m http.server <포트> --directory $DIR" >&2
exit 1
