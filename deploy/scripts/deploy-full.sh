#!/usr/bin/env bash
# 整站发布：API 容器 + 提示同步前端
# 用法：bash deploy/scripts/deploy-full.sh

set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/cyinc}"

cd "$APP_ROOT"
bash deploy/scripts/deploy.sh

if [[ ! -f "$APP_ROOT/myweb/index.html" ]]; then
  echo ""
  echo "WARN: $APP_ROOT/myweb/index.html 不存在"
  echo "请在本机执行: npm run build && bash deploy/scripts/sync-frontend.sh user@ecs"
  echo "或推送 main 触发 GitHub Actions deploy-ecs.yml"
fi
