#!/usr/bin/env bash
# 将本地 npm run build 产物 docs/ 同步到 ECS
# 用法：bash deploy/scripts/sync-frontend.sh [user@host]
# 环境变量：FRONTEND_DEST（默认 /var/www/cyinc/myweb/）

set -euo pipefail

TARGET="${1:?用法: bash deploy/scripts/sync-frontend.sh deploy@your-ecs-ip}"
DEST="${FRONTEND_DEST:-/var/www/cyinc/myweb/}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ ! -f "$ROOT/docs/index.html" ]]; then
  echo "ERROR: 未找到 $ROOT/docs/index.html，请先 npm run build" >&2
  exit 1
fi

echo "==> rsync docs/ -> $TARGET:$DEST"
rsync -avz --delete \
  -e ssh \
  "$ROOT/docs/" \
  "$TARGET:$DEST"

echo "Frontend synced."
