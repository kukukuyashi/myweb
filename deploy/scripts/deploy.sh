#!/usr/bin/env bash
# CYINC M6 — 拉代码并重建 API 容器
# 用法：bash deploy/scripts/deploy.sh
# CI 通过 SSH 调用此脚本

set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/cyinc}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
elif docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
else
  echo "ERROR: 未找到 docker-compose 或 docker compose 插件" >&2
  echo "请在 ECS 执行: sudo apt-get install -y docker-compose-plugin" >&2
  exit 1
fi

echo "==> 使用 ${COMPOSE[*]}"

cd "$APP_ROOT"

echo "==> git pull"
git fetch origin
git reset --hard origin/main

ENV_FILE="$APP_ROOT/backend/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: 缺少 $ENV_FILE，请先按 backend/.env.production.example 创建" >&2
  exit 1
fi
if grep -qE 'rm-xxxxx|强密码' "$ENV_FILE" 2>/dev/null; then
  echo "ERROR: backend/.env 仍含占位符（rm-xxxxx / 强密码），请改为真实 RDS 内网地址与 ASCII 密码" >&2
  exit 1
fi

echo "==> docker compose build & up"
"${COMPOSE[@]}" -f "$COMPOSE_FILE" build api
if ! "${COMPOSE[@]}" -f "$COMPOSE_FILE" up -d --force-recreate --remove-orphans; then
  echo "==> 常规 up 失败，清理冲突容器后重试" >&2
  "${COMPOSE[@]}" -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
  docker rm -f cyinc_redis_1 cyinc_api_1 2>/dev/null || true
  "${COMPOSE[@]}" -f "$COMPOSE_FILE" up -d --build --remove-orphans
fi

echo "==> 等待健康检查"
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8000/api/health >/dev/null; then
    echo "API healthy"
    "${COMPOSE[@]}" -f "$COMPOSE_FILE" ps
    exit 0
  fi
  sleep 2
done

echo "ERROR: API health check failed" >&2
"${COMPOSE[@]}" -f "$COMPOSE_FILE" logs --tail=50 api
exit 1
