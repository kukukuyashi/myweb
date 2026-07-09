#!/usr/bin/env bash
# CYINC M6 — 阿里云 ECS 首次初始化（Ubuntu 22.04+）
# 用法：sudo bash deploy/scripts/setup-server.sh

set -euo pipefail

DEPLOY_USER="${DEPLOY_USER:-deploy}"
APP_ROOT="${APP_ROOT:-/var/www/cyinc}"
REPO_URL="${REPO_URL:-https://github.com/YOUR_USER/gerenboke.git}"

echo "==> 安装系统包"
apt-get update
apt-get install -y git nginx certbot python3-certbot-nginx ufw

echo "==> 安装 Docker"
if ! command -v docker &>/dev/null; then
  curl -fsSL https://get.docker.com | sh
fi
apt-get install -y docker-compose-plugin

echo "==> 创建部署用户与目录"
id "$DEPLOY_USER" &>/dev/null || useradd -m -s /bin/bash "$DEPLOY_USER"
usermod -aG docker "$DEPLOY_USER"
mkdir -p "$APP_ROOT"
mkdir -p "$APP_ROOT/myweb"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_ROOT"

echo "==> 防火墙"
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

echo "==> Nginx 站点占位"
if [[ ! -f /etc/nginx/sites-available/cyinc ]]; then
  cp "$APP_ROOT/deploy/nginx.conf.example" /etc/nginx/sites-available/cyinc 2>/dev/null || true
  ln -sf /etc/nginx/sites-available/cyinc /etc/nginx/sites-enabled/cyinc
  rm -f /etc/nginx/sites-enabled/default
fi

cat <<EOF

========================================
首次初始化完成。请以 $DEPLOY_USER 用户继续：

  sudo -u $DEPLOY_USER -H bash -lc '
    cd $APP_ROOT
    git clone $REPO_URL .
    cp backend/.env.production.example backend/.env
    # 编辑 backend/.env（RDS、SECRET_KEY、CORS、Dify/n8n）
    nano backend/.env
    python3 -m venv backend/.venv
    backend/.venv/bin/pip install -r backend/requirements.txt
    backend/.venv/bin/python backend/scripts/gen_admin_password.py
    docker compose -f docker-compose.prod.yml up -d --build
  '

  sudo cp $APP_ROOT/deploy/nginx.conf.example /etc/nginx/sites-available/cyinc
  # 修改 server_name 后：
  sudo nginx -t && sudo systemctl reload nginx
  sudo certbot --nginx -d yourdomain.com

  # 本机 build 后同步前端：
  #   npm run build && bash deploy/scripts/sync-frontend.sh deploy@ECS_IP

冒烟（在 ECS 上）：
  curl -s http://127.0.0.1:8000/api/health
========================================
EOF
