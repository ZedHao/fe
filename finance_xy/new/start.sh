#!/bin/bash
# 猪猪基金 new 项目一键启动：检查依赖 → 释放端口 → 启动前后端

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SERVER_DIR="$ROOT/server"
CLIENT_DIR="$ROOT/client"
BACKEND_PORT="${BACKEND_PORT:-9001}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
PID_DIR="$ROOT/.pids"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "错误: 未找到命令 $1，请先安装"
    exit 1
  fi
}

ensure_python_deps() {
  log "检查 Python 依赖..."
  if python3 -c "import django, corsheaders" >/dev/null 2>&1; then
    log "Python 依赖已就绪"
    return
  fi
  log "安装 Python 依赖..."
  python3 -m pip install -r "$SERVER_DIR/requirements.txt"
}

ensure_node_deps() {
  log "检查 Node 依赖..."
  if [ -d "$CLIENT_DIR/node_modules" ] && [ -f "$CLIENT_DIR/node_modules/vue/package.json" ]; then
    log "Node 依赖已就绪"
    return
  fi
  log "安装 Node 依赖..."
  (cd "$CLIENT_DIR" && npm install)
}

free_port() {
  local port="$1"
  local pids
  pids="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [ -z "$pids" ]; then
    log "端口 $port 空闲"
    return
  fi
  log "端口 $port 被占用，正在结束进程: $pids"
  # shellcheck disable=SC2086
  kill -9 $pids 2>/dev/null || true
  sleep 1
}

start_backend() {
  log "启动后端 Django (端口 $BACKEND_PORT)..."
  mkdir -p "$PID_DIR"
  (cd "$SERVER_DIR" && python3 manage.py runserver "0.0.0.0:$BACKEND_PORT") \
    >"$PID_DIR/backend.log" 2>&1 &
  echo $! >"$PID_DIR/backend.pid"
}

start_frontend() {
  log "启动前端 Vite (端口 $FRONTEND_PORT)..."
  (cd "$CLIENT_DIR" && npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT") \
    >"$PID_DIR/frontend.log" 2>&1 &
  echo $! >"$PID_DIR/frontend.pid"
}

wait_for_port() {
  local port="$1"
  local name="$2"
  local i
  for i in $(seq 1 30); do
    if lsof -tiTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
      log "$name 已在端口 $port 监听"
      return 0
    fi
    sleep 0.5
  done
  echo "错误: $name 启动超时，请查看 $PID_DIR/${name}.log"
  exit 1
}

cleanup() {
  log "正在停止服务..."
  [ -f "$PID_DIR/backend.pid" ] && kill "$(cat "$PID_DIR/backend.pid")" 2>/dev/null || true
  [ -f "$PID_DIR/frontend.pid" ] && kill "$(cat "$PID_DIR/frontend.pid")" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

main() {
  require_cmd python3
  require_cmd npm
  require_cmd lsof

  ensure_python_deps
  ensure_node_deps

  free_port "$BACKEND_PORT"
  free_port "$FRONTEND_PORT"

  start_backend
  start_frontend

  wait_for_port "$BACKEND_PORT" "backend"
  wait_for_port "$FRONTEND_PORT" "frontend"

  echo ""
  echo "========================================"
  echo "  猪猪基金 前后端已启动"
  echo "========================================"
  echo "  前端:  http://localhost:$FRONTEND_PORT"
  echo "  后端:  http://localhost:$BACKEND_PORT"
  echo "  日志:  $PID_DIR/backend.log"
  echo "         $PID_DIR/frontend.log"
  echo "  停止:  Ctrl+C 或 kill \$(cat $PID_DIR/backend.pid) \$(cat $PID_DIR/frontend.pid)"
  echo "========================================"
  echo ""
  tail -f "$PID_DIR/backend.log" "$PID_DIR/frontend.log"
}

main "$@"
