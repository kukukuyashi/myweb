# ECS 上线状态（会话快照）

> 最后更新：2026-07-12 · 供排障与接手参考，非对外文档。

## 环境

| 项 | 值 |
|----|-----|
| ECS IP | `8.138.238.171` |
| 部署路径 | `/var/www/cyinc` |
| Compose | **`docker-compose`**（无 `docker compose` 插件） |
| GitHub Secrets | `ECS_HOST` / `ECS_USER`(root) / `ECS_SSH_KEY` 已配 |

## 当前线上状态

- **`/api/health` → 502**（nginx 正常，API 容器未就绪或已退出）
- 末次 **成功** Actions：`29188709304`（10:11，容器冲突修复后论坛可用）
- 末次 **失败** Actions：`29188989509` / `29188988362`（10:21，追番优化部署，健康检查失败）

## 根因（按时间）

1. 部署脚本先 `down` + `docker rm`，新 API 起不来 → 全站 502
2. `DATABASE_URL` 密码含中文 → `UnicodeEncodeError: latin-1`（用户已改）
3. **`DATABASE_URL` 主机仍为占位符 `rm-xxxxx.mysql.rds.aliyuncs.com`** → MySQL 连不上，API 启动失败

## 恢复步骤（ECS Workbench / root）

```bash
cd /var/www/cyinc
nano backend/.env
# DATABASE_URL 改为阿里云 RDS 真实内网地址，密码仅英文数字
# 例：mysql+pymysql://cyinc:YourPass@rm-bp1xxxx.mysql.rds.aliyuncs.com:3306/cyinc
# RDS 白名单需含 ECS 内网 IP

docker-compose -f docker-compose.prod.yml up -d --build
sleep 15
curl -s http://127.0.0.1:8000/api/health
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs --tail=40 api
```

验收：

- `http://8.138.238.171/api/health`
- `http://8.138.238.171/myweb/app/forum`
- `http://8.138.238.171/myweb/app/anime`

## 代码侧已做、待 ECS 拉取生效

| 改动 | 说明 |
|------|------|
| `bangumi_client.py` | 追番表 6h 缓存；`live_suggest=False` 跳过实时 mgnacg |
| `mgnacg_client.py` | fallback `mgnacg_vod_id` 直链；live suggest 可关 |
| `platform.js` | `/anime/schedule` 超时 30s |
| `deploy.sh` | `docker-compose` 兼容；部署前 `.env` 占位符检查；优先 `force-recreate` 避免先 down |
| `deploy-ecs.yml` | SSH 30m 超时；部署前 `git reset --hard origin/main` |

## 本机与 GitHub

- 本机 `git push` 曾失败（443）；可用 `gh api` 或网络恢复后 push
- **勿提交**：`backend/.env`、`frontend.zip`、`probe_*.py` 输出

## 相关文档

- [DEPLOY-PLAN.md](./DEPLOY-PLAN.md) · [README-m6-ecs.md](./README-m6-ecs.md)
