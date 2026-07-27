#!/usr/bin/env bash
# CYINC ECS 日常更新：拉代码 + 同步前端 + 重建 API
# 用法（ECS Workbench / SSH）：
#   cd /var/www/cyinc && bash deploy/scripts/ecs-update.sh

set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/cyinc}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
BRANCH="${BRANCH:-main}"

cd "$APP_ROOT"

# 鍏煎 docker-compose(v1) 涓?docker compose(v2)
if docker compose version >/dev/null 2>&1; then
  DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  DC="docker-compose"
else
  echo "ERROR: neither 'docker compose' nor 'docker-compose' found" >&2
  exit 1
fi
echo "==> using compose command: $DC"

echo "==> git pull ($BRANCH)"
git fetch origin
git reset --hard "origin/$BRANCH"

# 运行时数据（posts.json + Content/）住在独立的 site-data/，与 myweb/ 物理隔离
SITE_DATA="${SITE_DATA:-$APP_ROOT/site-data}"
mkdir -p "$SITE_DATA/Content" "$SITE_DATA/data"

echo "==> sync frontend docs/ -> myweb/ (runtime data lives in site-data/, untouched)"
mkdir -p myweb
# 前端构建产物里的 posts.json/Content 仅为占位，真正运行数据在 site-data/
rsync -a --delete \
  --exclude='data/posts.json' \
  --exclude='Content/' \
  --exclude='uploads/' \
  docs/ myweb/

echo "==> seed git-tracked Content/*.html -> site-data/Content (add/update, never delete)"
if ls Content/*.html >/dev/null 2>&1; then
  cp -f Content/*.html "$SITE_DATA/Content/"
fi
# 首次迁移：若 site-data 空而旧 myweb 有数据，先搬过来（只补不覆盖）
if [ ! -s "$SITE_DATA/data/posts.json" ] && [ -s myweb/data/posts.json ]; then
  echo "   migrate myweb/data/posts.json -> site-data/data/"
  cp -n myweb/data/posts.json "$SITE_DATA/data/posts.json"
fi
if [ -d myweb/Content ]; then
  cp -rn myweb/Content/. "$SITE_DATA/Content/" 2>/dev/null || true
fi

echo "==> docker compose build & up"
# docker-compose v1.29.2 recreate 有 ContainerConfig bug，改用 build + stop + rm + up 规避
$DC -f "$COMPOSE_FILE" build api
$DC -f "$COMPOSE_FILE" up -d --no-recreate redis
$DC -f "$COMPOSE_FILE" stop api || true
$DC -f "$COMPOSE_FILE" rm -f api || true
$DC -f "$COMPOSE_FILE" up -d --no-deps api

echo "==> wait for API health"
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8000/api/health >/dev/null; then
    echo "API healthy"
    $DC -f "$COMPOSE_FILE" ps
    echo "Frontend index:"
    head -c 200 myweb/index.html || true
    echo
    exit 0
  fi
  sleep 2
done

echo "ERROR: API health check failed" >&2
$DC -f "$COMPOSE_FILE" logs --tail=80 api
exit 1
