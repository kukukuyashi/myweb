# CYINC · ECS 部署执行计划

> 更新：2026-07-10  
> 目标：`https://你的域名/myweb/` + `/api/v1` + `/admin` 同域上线  
> 详细手册：[README-m6-ecs.md](./README-m6-ecs.md)

---

## 当前状态

| 项目 | 状态 |
|------|------|
| M1–M5.5 功能（API / 论坛 / 番茄钟 / 个人中心） | ✅ 本地完成 |
| M6 部署脚本（Docker / Nginx / GitHub Actions） | ✅ 仓库已有 |
| 上次推送到 GitHub `main` | `1e628bb`（2026-07-10） |
| 本地未提交 | 弹匣计时 UI、`pomoTimerSegments.js` 等 |
| ECS 是否已初始化 | ⬜ 请你确认 |

---

## 阶段 0 · 本机发布前（Windows，约 30 分钟）

### 0.1 本地冒烟

```powershell
cd D:\phpstudy\phpstudy_pro\WWW\gerenboke\backend
.\scripts\smoke-test.ps1
.\scripts\smoke-test-posts.ps1
.\scripts\smoke-test-forum.ps1
.\scripts\smoke-test-qa.ps1
```

### 0.2 构建前端

```powershell
cd D:\phpstudy\phpstudy_pro\WWW\gerenboke
Copy-Item .env.production.example .env.production -ErrorAction SilentlyContinue
npm run build
```

确认：`docs/index.html` 存在，且无报错。

### 0.3 提交并推送（勿含密钥）

**可提交：**

- `src/`、`docs/`（build 产物）
- `deploy/`、`docker-compose.prod.yml`
- `backend/.env.example`、`backend/.env.production.example`

**绝不提交：**

- `backend/.env`、`.env.production`
- `backend/uploads/`、`img/BA/`、`frontend.zip`

```powershell
git add src docs deploy docker-compose.prod.yml backend/.env.example backend/.env.production.example
git status   # 确认无 .env
git commit -m "feat: 弹匣计时 UI + M6 部署计划"
git push origin main
```

> 若当前在 `feat/platform-v2-fastapi`：先 merge 到 `main` 再 push。

### 0.4 GitHub Actions Secrets（推荐自动部署）

仓库 → **Settings → Secrets and variables → Actions**

| Secret | 说明 |
|--------|------|
| `ECS_HOST` | ECS 公网 IP 或域名 |
| `ECS_USER` | SSH 用户，如 `deploy` |
| `ECS_SSH_KEY` | 私钥全文（对应 ECS `~/.ssh/authorized_keys`） |

可选 **Variables**：

| Variable | 示例 |
|----------|------|
| `VITE_MUSIC_BASE_URL` | 留空 = 同域 `/myweb/Music/` |
| `VITE_TWIKOO_ENV_ID` | Twikoo 云函数 URL |

配置完成后：推 `main` → 自动 build + rsync 前端 + SSH 跑 `deploy/scripts/deploy.sh`。

---

## 阶段 1 · 阿里云资源（首次，约 1–2 天 + 备案等待）

### 1.1 购买 / 确认

- [ ] **ECS**：Ubuntu 22.04，2C2G+，40G 系统盘
- [ ] **RDS MySQL 8**：库名 `cyinc`，utf8mb4，与 ECS **同地域**
- [ ] **域名**：A 记录 → ECS 公网 IP
- [ ] **备案**（大陆 ECS 必须）：阿里云备案控制台提交

### 1.2 安全组

| 端口 | 用途 |
|------|------|
| 22 | SSH |
| 80 | HTTP（Certbot / 跳转 HTTPS） |
| 443 | HTTPS |

**不要**对 0.0.0.0/0 开放：8000、3306、6379。

### 1.3 RDS 白名单

- [ ] 加入 ECS **内网 IP**
- [ ] 记录连接串：`rm-xxxxx.mysql.rds.aliyuncs.com`

---

## 阶段 2 · ECS 首次初始化（SSH，约 1 小时）

### 2.1 登录与克隆

```bash
ssh root@你的ECS_IP
adduser deploy && usermod -aG sudo deploy
# 配置 deploy 的 SSH 公钥

sudo mkdir -p /var/www/cyinc
sudo chown deploy:deploy /var/www/cyinc
su - deploy
git clone https://github.com/kukukuyashi/myweb.git /var/www/cyinc
cd /var/www/cyinc
```

### 2.2 安装 Docker / Nginx

```bash
sudo bash deploy/scripts/setup-server.sh
```

### 2.3 生产 `backend/.env`（只在服务器上编辑）

```bash
cp backend/.env.production.example backend/.env
nano backend/.env
```

**必填项核对：**

```env
DATABASE_URL=mysql+pymysql://cyinc:密码@rm-xxxxx.mysql.rds.aliyuncs.com:3306/cyinc
SECRET_KEY=<openssl rand -hex 32>
CORS_ORIGINS=https://你的域名.com
PUBLIC_SITE_URL=https://你的域名.com/myweb
REDIS_URL=redis://redis:6379/0

DIFY_SUMMARY_API_KEY=app-xxx
DIFY_CHAT_API_KEY=app-yyy
N8N_WEBHOOK_URL=https://xxx.app.n8n.cloud/webhook/...

# 若开启邮箱注册验证码
SMTP_PASSWORD=<QQ邮箱授权码>
```

生成 Admin 密码：

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
backend/.venv/bin/python backend/scripts/set_admin_password.py "你的强密码"
# 把输出的 hash 填入 .env 的 ADMIN_PASSWORD_HASH=
```

### 2.4 启动 API + Redis

```bash
docker compose -f docker-compose.prod.yml up -d --build
curl -s http://127.0.0.1:8000/api/health
```

### 2.5 Nginx

```bash
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/cyinc
sudo nano /etc/nginx/sites-available/cyinc   # 改 server_name
sudo ln -sf /etc/nginx/sites-available/cyinc /etc/nginx/sites-enabled/cyinc
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

### 2.6 首次同步前端（本机 Windows）

**方式 A — GitHub Actions**（Secrets 已配）：推 `main` 后等 Actions 绿。

**方式 B — 手动 zip：**

```powershell
cd D:\phpstudy\phpstudy_pro\WWW\gerenboke
.\deploy\scripts\pack-frontend.ps1
scp frontend.zip deploy@ECS_IP:/var/www/cyinc/
```

```bash
cd /var/www/cyinc/myweb && unzip -o ../frontend.zip
```

**方式 C — rsync（Git Bash / WSL）：**

```bash
bash deploy/scripts/sync-frontend.sh deploy@ECS_IP
```

### 2.7 静态资源（不进 Git 的大文件）

```bash
# 本机 rsync 到 ECS（ACG 图、音乐）
rsync -avz img/ deploy@ECS_IP:/var/www/cyinc/img/
rsync -avz Music/ deploy@ECS_IP:/var/www/cyinc/Music/
```

Nginx 需 alias `/myweb/img/`、`/myweb/Music/`（见 `nginx.conf.example`）。

### 2.8 HTTPS（备案通过后）

```bash
sudo certbot --nginx -d 你的域名.com -d www.你的域名.com
```

---

## 阶段 3 · 上线验收（15 分钟）

- [ ] `https://域名/myweb/` — 博客首页
- [ ] `https://域名/myweb/app` — 主站 Hub
- [ ] `https://域名/myweb/app/pomo` — 番茄钟（弹匣/能量格）
- [ ] `https://域名/myweb/app/me` — 登录、改密、头像
- [ ] `https://域名/myweb/app/forum` — 论坛
- [ ] `https://域名/api/health` — `{"status":"ok"}` 或类似
- [ ] `https://域名/admin` — SQLAdmin 登录
- [ ] 注册 → 登录 → 发文 → n8n Executions 有记录
- [ ] `/ai` 助手可对话（Dify Key 已填）
- [ ] 头像上传后刷新仍可见

---

## 阶段 4 · 日常更新

### 改前端 + 后端（推荐）

```text
本机：git push origin main
→ GitHub Actions 自动 build + rsync + deploy.sh
```

### 仅改后端

```bash
ssh deploy@ECS_IP
cd /var/www/cyinc && bash deploy/scripts/deploy.sh
```

### 仅改前端（无 Actions 时）

```powershell
npm run build
bash deploy/scripts/sync-frontend.sh deploy@ECS_IP
```

### 改 `backend/.env` 后

```bash
# ECS 常用 docker-compose（无 compose 插件时）
docker-compose -f docker-compose.prod.yml up -d --build api
```

线上排障快照见 [ECS-STATUS.md](./ECS-STATUS.md)。

---

## 阶段 5 · 数据迁移（可选）

本地 phpStudy 已有数据时：

```powershell
# 本机导出
mysqldump -uCyinc -p cyinclog > cyinc_backup.sql
scp cyinc_backup.sql deploy@ECS_IP:/tmp/
```

```bash
# ECS 导入 RDS
mysql -h rm-xxxxx.mysql.rds.aliyuncs.com -u cyinc -p cyinc < /tmp/cyinc_backup.sql
```

全新上线可跳过，API 首次启动自动建表 + seed 论坛板块。

---

## 风险与决策

| 问题 | 建议 |
|------|------|
| 备案未完成 | 先用 IP + HTTP 内测 API；域名 HTTPS 等备案 |
| 无 RDS | 短期可在 ECS Docker 跑 MySQL（不推荐长期） |
| GitHub Pages 与 ECS 并存 | 正式运营以 ECS 为准；Pages 可做跳转或停更 |
| Dify/n8n | 继续用 Cloud，Key 只写 ECS 的 `backend/.env` |
| 音乐/大图 | ECS 上 `img/`、`Music/` 单独 rsync，不进 Git |

---

## 下一步（请你拍板）

1. **ECS / RDS / 域名是否已有？** 有 → 从阶段 2 开始；无 → 阶段 1  
2. **GitHub Actions Secrets 是否已配？** 有 → 推 `main` 即可；无 → 阶段 0.4  
3. **本机未提交的弹匣 UI 是否先 commit？** 建议先提交再部署  

相关文档：[README-m6-ecs.md](./README-m6-ecs.md) · [README-cloud-dev.md](./README-cloud-dev.md) · [backend/README.md](../backend/README.md)
