# CYINC FastAPI Backend

个人全栈平台后端 · FastAPI + MySQL + Redis（可选）+ Dify / n8n 集成。

| 里程碑 | 内容 | 状态 |
|--------|------|------|
| M1 | 用户注册 / 登录 / JWT | ✅ |
| M2 | 文章 CRUD + Redis 列表缓存 | ✅ |
| M3 | Dify Cloud 摘要 + `/ai` 助手 | ✅（需填 Cloud Key） |
| M4 | n8n Cloud 发文 Webhook | ✅（需填 Webhook URL） |
| M5 | Hub + `/me` + 番茄钟 | ✅ |
| M5.5 | 论坛 MVP + 留言板 Q&A + 番茄钟时间线 | ✅ |
| **M6** | **阿里云 ECS + Docker + Nginx + HTTPS** | 📦 见 [deploy/README-m6-ecs.md](../deploy/README-m6-ecs.md) |

---

## 前置条件

1. **phpStudy 里 MySQL 已启动**（首页看到 MySQL 5.7.26 运行中）
2. 知道 **root 密码**（phpStudy → **数据库** → 查看或修改 root 密码）
3. Python 3.10+、backend 虚拟环境已安装依赖

> **重要**：MySQL 只能通过 phpStudy 面板启动。不要手动运行 `mysqld.exe`，否则会占用 3306 端口或锁 `ibdata1`，导致 phpStudy 里的 MySQL 自动退出。

---

## 一、建库与 `.env`

phpStudy 自带 `mysql.exe`：

```
D:\phpstudy\phpstudy_pro\Extensions\MySQL5.7.26\bin\mysql.exe
```

### 方式 A：使用 phpStudy 已有库（推荐）

phpStudy → **数据库** 页面里若已有库（例如 `cyinclog` / 用户 `Cyinc`），直接写 `backend/.env`：

```env
DATABASE_URL=mysql+pymysql://Cyinc:你的密码@127.0.0.1:3306/cyinclog
```

启动 API 后会自动建表并 seed 论坛板块。

### 方式 B：一键脚本（root 新建 cyinc 库）

```powershell
cd backend
.\scripts\setup-db.ps1 -Password "你的密码"
```

### 方式 C：纯 mysql 命令行

```sql
CREATE DATABASE IF NOT EXISTS cyinc
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

复制 `.env.example` 为 `.env` 并填写 `DATABASE_URL`、`SECRET_KEY` 等。

**生产环境**：复制 `.env.production.example`，详见 [deploy/README-m6-ecs.md](../deploy/README-m6-ecs.md)。

---

## 二、安装依赖并启动

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 任选一种启动（推荐前两种，带 --reload 改代码自动重启）
npm run dev:api                              # 项目根目录
.\scripts\dev.ps1                            # backend 目录
.\dev.bat                                    # 双击或 cmd
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

启动成功标志：终端出现 `Application startup complete`，无 MySQL 连接报错。

| 入口 | URL |
|------|-----|
| 健康检查 | <http://127.0.0.1:8000/api/health> |
| Swagger | <http://127.0.0.1:8000/api/docs> |
| SQLAdmin | <http://127.0.0.1:8000/admin> |

---

## 三、数据管理（三层）

| 层级 | 工具 | 用途 |
|------|------|------|
| 运维后台 | **SQLAdmin** `/admin` | 浏览器管理用户、文章、论坛、留言板 |
| 业务 API | **Swagger** `/api/docs` | 注册、发文、论坛、留言板等 |
| 数据库 | **mysql 命令行 / RDS DMS** | 紧急排查、批量 SQL |

### SQLAdmin 登录

1. 密码只存 bcrypt 哈希（`.env` 里 `ADMIN_PASSWORD_HASH`）
2. 强度：至少 9 位，含大写 + 小写 + 数字
3. 防暴力：15 分钟内错 5 次临时锁定
4. 会话：登录后 8 小时过期

```powershell
cd backend
.\.venv\Scripts\python scripts\gen_admin_password.py
# 或
.\.venv\Scripts\python scripts\set_admin_password.py "YourStrongPass123"
```

重启 uvicorn 后访问 <http://127.0.0.1:8000/admin>，用户名为 `ADMIN_USERNAME`（默认 `admin`）。

**管理后台菜单：**

| 菜单 | 管理员常用操作 |
|------|----------------|
| 用户 | 查看/改昵称头像、删除违规账号 |
| 文章 | 编辑/删除用户文章；`status=draft` 可下架 |
| 论坛板块 | 增删改板块 |
| 论坛帖子 | 置顶、锁定、删帖 |
| 论坛回复 | 删违规回复 |
| 留言板 | 删匿名留言 |

> 番茄钟记录暂无 Admin 入口。

---

## 四、冒烟测试

在 **backend** 目录、API 已启动时执行：

```powershell
.\scripts\smoke-test.ps1           # M1 鉴权
.\scripts\smoke-test-posts.ps1      # M2 文章 CRUD
.\scripts\smoke-test-forum.ps1     # M5.5 论坛发帖回帖
.\scripts\smoke-test-qa.ps1        # M5.5 留言板匿名提交
```

或在 Swagger `/api/docs` 里操作（Authorize 填 `Bearer <token>`）。

---

## 五、Redis（可选）

根目录 `docker-compose.yml` 仅含 Redis。有 Docker 时：

```powershell
docker compose up -d redis
```

`.env` 中设置 `REDIS_URL=redis://127.0.0.1:6379/0`。未安装 Docker 时 API **照常运行**，只是文章列表缓存不生效。

生产环境 Redis 由 `docker-compose.prod.yml` 一并启动，见 M6 文档。

---

## 六、API 一览

前缀均为 `/api/v1`（健康检查除外）。成功响应格式：

```json
{ "code": 0, "message": "ok", "data": { } }
```

### 系统

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/api/health` | 健康检查 | 否 |
| — | `/api/docs` | Swagger | 否 |
| — | `/admin` | SQLAdmin | Admin 会话 |

### 鉴权与用户

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/auth/register` | 注册 | 否 |
| POST | `/auth/login` | 登录 | 否 |
| GET | `/auth/me` | 当前用户 | Bearer |
| GET | `/users/me` | 个人资料 | Bearer |
| PATCH | `/users/me` | 更新资料 | Bearer |
| POST | `/users/me/avatar` | 上传头像（multipart） | Bearer |

### 文章（M2）

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/posts` | 已发布列表（Redis 缓存） | 否 |
| GET | `/posts/mine` | 我的文章含草稿 | Bearer |
| GET | `/posts/{id}` | 详情 | 否 |
| POST | `/posts` | 创建 | Bearer |
| PATCH | `/posts/{id}` | 更新（仅作者） | Bearer |
| DELETE | `/posts/{id}` | 删除（仅作者） | Bearer |
| POST | `/posts/{id}/summary` | Dify 生成摘要 | Bearer |

### 论坛（M5.5）

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/forum/categories` | 板块列表 | 否 |
| GET | `/forum/categories/{slug}/threads` | 板块内帖子 | 否 |
| GET | `/forum/threads/recent` | 最新帖子 | 否 |
| GET | `/forum/threads/mine` | 我的帖子 | Bearer |
| GET | `/forum/threads/{id}` | 帖子详情 + 回复 | 否 |
| POST | `/forum/threads` | 发帖 | Bearer |
| PATCH | `/forum/threads/{id}` | 编辑帖子（仅作者） | Bearer |
| DELETE | `/forum/threads/{id}` | 删除帖子（仅作者） | Bearer |
| POST | `/forum/threads/{id}/replies` | 回帖 | Bearer |

### 留言板 Q&A（M5.5）

主站首页「留言板」使用此 API（与博客 Twikoo 留言 `/guestbook` 独立）。

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/qa/messages` | 留言列表 | 否 |
| POST | `/qa/messages` | 提交留言（可匿名） | 可选 Bearer |

### 番茄钟（M5 / M5.5）

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/pomodoro/sessions` | 记录一次番茄钟 | Bearer |
| GET | `/pomodoro/sessions` | 我的记录 | Bearer |
| GET | `/pomodoro/stats` | 统计 | Bearer |
| GET | `/pomodoro/timeline` | 按日分组时间线 | Bearer |

### AI 与集成（M3 / M4）

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/ai/status` | Dify 配置是否就绪 | 否 |
| POST | `/ai/summary` | 文本摘要 | Bearer |
| POST | `/ai/chat` | 站内 AI 对话 | Bearer |
| GET | `/integrations/status` | Dify + n8n 状态 | 否 |

---

## 七、环境变量

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | MySQL 连接串（`mysql+pymysql://...`） |
| `SECRET_KEY` | JWT + Session 密钥（生产必须更换） |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期，默认 10080（7 天） |
| `CORS_ORIGINS` | 逗号分隔的前端 Origin |
| `API_PREFIX` | 默认 `/api/v1` |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD_HASH` | SQLAdmin |
| `REDIS_URL` | 可选，如 `redis://127.0.0.1:6379/0` |
| `DIFY_API_URL` / `DIFY_*_API_KEY` | Dify Cloud |
| `N8N_WEBHOOK_URL` / `N8N_WEBHOOK_SECRET` | n8n 发文通知 |
| `PUBLIC_SITE_URL` | 站点根 URL（n8n 通知链接用） |

完整示例见 `.env.example`（开发）与 `.env.production.example`（生产）。

---

## 八、相关文档

| 文档 | 用途 |
|------|------|
| [deploy/README-cloud-dev.md](../deploy/README-cloud-dev.md) | 方案 A：无本机 Docker，Dify / n8n Cloud |
| [deploy/README-dify.md](../deploy/README-dify.md) | ECS 自建 Dify（M6 可选） |
| [deploy/README-m6-ecs.md](../deploy/README-m6-ecs.md) | **M6 整站 ECS 部署**（同域 `/myweb/` + `/api`） |
| [deploy/nginx.conf.example](../deploy/nginx.conf.example) | Nginx 反向代理示例 |
| [deploy/cyinc-api.service.example](../deploy/cyinc-api.service.example) | systemd 直跑 uvicorn（不用 Docker 时） |

---

## 九、与前端联调

前端 `.env`：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

请求头：`Authorization: Bearer <access_token>`

- 博客 / 主站 Vue：`npm run dev` → <http://localhost:5173/myweb/>
- 主站平台 Hub：<http://localhost:5173/myweb/app>
- AI 页：<http://localhost:5173/myweb/ai>

生产构建后前端可继续走 GitHub Pages，API 走 ECS 域名；或前后端同域部署，见 M6 文档。

---

## 十、常见问题

| 现象 | 处理 |
|------|------|
| `Can't connect to MySQL server on 127.0.0.1` | phpStudy 里启动 MySQL；勿手动起 mysqld |
| `Access denied for user 'root'` | 密码错，去 phpStudy 数据库页改/查 |
| `Unknown database 'cyinc'` | 执行 `scripts/init-db.sql` 或 `setup-db.ps1` |
| 注册 500 / bcrypt 报错 | `pip install passlib[bcrypt]` 或确认 `bcrypt` 已装 |
| Dify `summary_ready: false` | 检查 `.env` 中 `DIFY_*_API_KEY`，见 cloud-dev 文档 |
| CORS 报错 | 把前端 Origin 加入 `CORS_ORIGINS` |
| `/pomodoro/timeline` 401 | 需登录，带 Bearer Token |

---

## 十一、目录结构

```
backend/
├── app/
│   ├── main.py           # 入口、CORS、Admin、建表
│   ├── api/v1/           # 路由：auth users posts forum qa pomodoro ai
│   ├── admin/            # SQLAdmin
│   ├── core/             # config db security response
│   ├── models/           # SQLAlchemy 模型
│   ├── schemas/          # Pydantic
│   └── services/         # cache dify n8n forum_seed
├── scripts/              # 建库、冒烟测试、Admin 密码
├── Dockerfile            # M6 容器镜像
├── requirements.txt
├── .env.example
└── .env.production.example
```
