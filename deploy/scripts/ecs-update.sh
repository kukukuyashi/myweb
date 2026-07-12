#!/usr/bin/env bash
# CYINC ECS 日常更新：拉代码 + 同步前端 + 重建 API
# 用法（ECS Workbench / SSH）：
#   cd /var/www/cyinc && bash deploy/scripts/ecs-update.sh

set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/cyinc}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
BRANCH="${BRANCH:-main}"

cd "$APP_ROOT"

echo "==> git pull ($BRANCH)"
git fetch origin
git reset --hard "origin/$BRANCH"

echo "==> sync frontend docs/ -> myweb/"
mkdir -p myweb
rsync -a --delete docs/ myweb/

echo "==> sync Content/*.html (avoid Windows zip mojibake)"
mkdir -p myweb/Content
cp -f Content/*.html myweb/Content/

echo "==> docker compose build & up"
docker compose -f "$COMPOSE_FILE" up -d --build --remove-orphans

echo "==> wait for API health"
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8000/api/health >/dev/null; then
    echo "API healthy"
    docker compose -f "$COMPOSE_FILE" ps
    echo "Frontend index:"
    head -c 200 myweb/index.html || true
    echo
    exit 0
  fi
  sleep 2
done

echo "ERROR: API health check failed" >&2
docker compose -f "$COMPOSE_FILE" logs --tail=80 api
exit 1
