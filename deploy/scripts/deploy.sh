#!/usr/bin/env bash
# CYINC M6 — 拉代码并重建 API 容器
# 用法：bash deploy/scripts/deploy.sh
# CI 通过 SSH 调用此脚本

set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/cyinc}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

cd "$APP_ROOT"

echo "==> git pull"
git fetch origin
git reset --hard origin/main

echo "==> docker compose build & up"
docker compose -f "$COMPOSE_FILE" up -d --build --remove-orphans

echo "==> 等待健康检查"
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8000/api/health >/dev/null; then
    echo "API healthy"
    docker compose -f "$COMPOSE_FILE" ps
    exit 0
  fi
  sleep 2
done

echo "ERROR: API health check failed" >&2
docker compose -f "$COMPOSE_FILE" logs --tail=50 api
exit 1
