# CYINC 动态主站 · 求职向工作流

> 版本：v2.0 · 2026-07-05  
> 目标：将 CYINC.LOG 演进为 **AI 增强型全栈个人平台**，对齐「Python + Vue + MySQL + Dify + N8N + Docker + 云部署」类岗位 JD。  
> **AI 方案：Dify Cloud（方案 A）** · 本地无需 Docker · Docker 留 M6 阿里云 ECS

---

## 方案 A 说明（当前采用）

| 层级 | 本地 Windows | 云服务 |
|------|-------------|--------|
| MySQL | phpstudy | M6 → RDS |
| FastAPI / Vue | 本机开发 | M6 → ECS |
| Dify | — | **cloud.dify.ai** |
| N8N | — | **n8n.io 云 Webhook** |
| Redis | 可选跳过 | M6 → ECS / 云 Redis |
| Docker | **本机不装** | M6 → Ubuntu ECS |

详细步骤：[deploy/README-cloud-dev.md](../deploy/README-cloud-dev.md)

---

## 〇、目标岗位能力对照

| JD 要求 | 本项目对应 | Phase |
|---------|-----------|-------|
| Cursor / AI 协作开发 | 全程 Cursor 辅助，README 记录协作流程 | 贯穿 |
| **Dify LLMOps 工作流** | 自建 Dify，文章摘要 + 站内 AI 助手 | **A** |
| **N8N 工作流自动化** | 发文 Webhook → 通知/归档 | **A** |
| Python | FastAPI 后端 | A |
| Vue / CSS | 现有 CYINC.LOG 前端 | A |
| MySQL | 业务主库 | A |
| **Redis** | 文章列表缓存 / API 限流 | **A** |
| **Docker** | docker-compose 编排本地全家桶 | **A** |
| Nginx + 服务器部署 | 阿里云 ECS 生产环境 | A |
| Git 协作 | GitHub + 功能分支 | 贯穿 |

**论坛 MVP 已提前至 M5.5** — 主站 `/app` 与博客 `/` 路由分离，账号共用 JWT。

---

## 一、项目愿景与求职定位

### 1.1 一句话描述

**将 CYINC.LOG 升级为 AI 增强型个人平台：Vue 3 + FastAPI + MySQL + Redis，集成自建 Dify 工作流与 N8N 自动化，Docker 本地编排，阿里云 ECS 生产部署。**

### 1.2 简历目标句

> 使用 Cursor 协作完成 Vue 3 + FastAPI 全栈平台；自建 Dify 实现文章摘要与站内 AI 问答；N8N 搭建发布自动化链路；Docker Compose 编排 MySQL/Redis/Dify/N8N；Nginx 部署于阿里云 ECS。

### 1.3 已有资产

| 维度 | 现状 | 面试信号 |
|------|------|----------|
| 前端 | Vue 3 + Vite + Pinia，~28 篇，prerender/SEO | SPA 工程化 |
| CI/CD | GitHub Actions | 自动化意识 |
| 产品感 | 时间轴、自定义光标、音乐室 | UI/交互独立完成 |
| Python | Flask + 通义千问（陈皮有多陈） | AI 调用基础 → 升级到 Dify 编排 |
| 后端 M1 | FastAPI 注册/登录/JWT 脚手架 | Python 后端已起步 |

在线 demo（静态版）：<https://kukukuyashi.github.io/myweb/>

### 1.4 当前缺口

- [x] M1：FastAPI 鉴权脚手架（`feat/platform-v2-fastapi` 分支）
- [x] M2：文章 CRUD + Redis 缓存（无 Docker 时自动降级直连 MySQL）
- [x] M3：Dify API 对接 + `/ai` 页（**填 Dify Cloud Key 即可**）
- [x] M4：N8N 发文 Webhook（**填 n8n Cloud URL 即可**）
- [x] M5：Hub + `/me` + 番茄钟 + `/forum` 占位
- [x] M5.5：主站 `/app` 分离 + 论坛 MVP + 番茄钟 v2 + 个人中心 Tab
- [ ] 阿里云 ECS 生产上线（**此处再学 Docker**）

---

## 二、已确认技术决策

| 层级 | 选型 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Vite + Pinia | 沿用现有仓库 |
| 后端 | **FastAPI** + Uvicorn | OpenAPI 文档化 |
| 业务库 | **MySQL 8** | phpstudy 本地 / RDS 生产 |
| 缓存 | **Redis 7** | 列表缓存、限流 |
| AI | **Dify Cloud**（本地）/ 自建（ECS） | Workflow + Chatflow |
| 自动化 | **n8n Cloud**（本地）/ 自建（ECS） | 发文 Webhook |
| 本地编排 | **无需 Docker** | Redis/Docker 仅 M6 ECS |
| 生产部署 | **阿里云 ECS** + Nginx + systemd | 静态 SPA + API 反代 |
| 开发工具 | **Cursor** + Navicat | AI 协作 + 本地 MySQL 管理 |
| LLM 模型 | Dify 内配置（通义/DeepSeek/OpenAI 等） | 通过 Dify 统一管理 Key，业务层不直连 |

### 架构图

```mermaid
flowchart TB
  Browser[浏览器]
  Nginx[Nginx_ECS]
  Vue[Vue3_SPA]
  API[FastAPI]
  Redis[(Redis)]
  MySQL[(MySQL)]
  Dify[Dify_自建]
  N8N[N8N_自建]
  LLM[LLM_通义等]

  Browser --> Nginx
  Nginx --> Vue
  Nginx --> API
  API --> MySQL
  API --> Redis
  API -->|Workflow_API| Dify
  Dify --> LLM
  API -->|Webhook| N8N
  N8N -->|通知邮件等| Notify[通知渠道]
```

### 路由规划（M5.5 更新）

| 路径 | 模块 | 说明 |
|------|------|------|
| `/` | 博客首页 | 现有 NavBar，独立气质 |
| `/archive` … | 博客子页 | 不变 |
| `/ai` | AI 助手 | 博客 NavBar 入口 |
| **`/app`** | **主站首页** | PlatformNav，论坛热帖 + 快捷入口 |
| `/app/forum` | 论坛板块 | 三板块 MVP |
| `/app/forum/c/:slug` | 板块帖子列表 | |
| `/app/forum/t/:id` | 帖子详情 + 回帖 | |
| `/app/forum/new` | 发帖 | 需登录 |
| `/app/me` | 个人中心 v2 | Tab：资料 / 文章 / 帖子 / 专注时间线 |
| `/app/pomo` | 番茄钟 v2 | 圆环、设置、全屏、通知、反思弹窗 |
| `/hub` → `/app` | 旧路由重定向 | 兼容 |
| `/me` `/pomo` `/forum` | 重定向至 `/app/*` | 兼容 |
| `/api/v1/*` | REST API | 含 `/forum/*`、`/pomodoro/timeline` |
| `/api/docs` | Swagger | |

---

## 三、Dify 自建方案（核心）

### 3.1 为什么选 Dify 自建

| 对比 | Dify 自建 | Coze |
|------|-----------|------|
| 部署 | Docker 一键，可放 ECS | 纯 SaaS |
| 与 FastAPI 对接 | REST API，后端统一封装 | 偏前端/SDK |
| 面试叙事 | 「LLMOps 平台自建 + API 集成」 | 「零代码配置」 |
| 与陈皮项目延续 | 从 Flask 直调模型 → Dify 工作流编排 | 关联弱 |

### 3.2 Dify 部署方式

**本地 / ECS 均用官方 Docker Compose：**

```bash
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
docker compose up -d
```

默认控制台：<http://localhost:3000>（首次注册管理员）

生产建议：

- Dify 与业务 API **同 ECS 不同端口**，Nginx 反代 `dify.yourdomain.com`（内网访问可不暴露公网）
- LLM API Key 只在 Dify 控制台配置，**不进 Git**

### 3.3 在 Dify 内创建的应用

#### 应用 1：文章摘要 Workflow（必做）

```
输入：title + content（Markdown/HTML 纯文本）
节点：LLM → 输出 100 字摘要 + 3 个标签建议
输出：JSON { summary, suggested_tags }
```

- 发布类型：**Workflow**
- FastAPI 调用：`POST {DIFY_API_URL}/v1/workflows/run`
- 触发时机：用户发布文章时（可选）或手动点「生成摘要」

#### 应用 2：站内 AI 助手 Chatflow（必做）

```
知识库：导入 CYINC 博客 Markdown/HTML 转文本
对话：基于知识库 RAG 回答「你写过哪些 Vue 文章？」等
```

- 发布类型：**Chatflow** + **Knowledge**
- FastAPI 调用：`POST {DIFY_API_URL}/v1/chat-messages`（streaming 可选）
- 前端：`/ai` 页面聊天 UI

#### 应用 3：番茄钟复盘 Workflow（可选）

```
输入：今日专注分钟数 + 完成的任务列表
输出：一句鼓励 + 明日建议
```

- 触发：番茄钟 session 写入后，FastAPI 异步调 Dify

### 3.4 FastAPI 封装层

```
backend/app/
  services/
    dify_client.py      # 统一 HTTP 调用、超时、重试、降级
  api/v1/
    ai.py               # POST /ai/summary, POST /ai/chat
```

**降级策略**（面试加分，陈皮项目延续）：

- Dify 超时 / 5xx → 返回「AI 暂不可用」，不阻塞发文
- 摘要失败 → `summary` 字段为空，文章照常发布

### 3.5 环境变量

```env
# backend/.env
DIFY_API_URL=http://127.0.0.1:5001
DIFY_SUMMARY_API_KEY=app-xxxxxxxx          # Workflow 应用 API Key
DIFY_CHAT_API_KEY=app-yyyyyyyy             # Chatflow 应用 API Key
DIFY_TIMEOUT_SEC=30
```

### 3.6 posts 表扩展

| 字段 | 类型 | 说明 |
|------|------|------|
| ai_summary | VARCHAR(500) NULL | Dify 生成的摘要 |
| ai_summary_at | DATETIME NULL | 摘要生成时间 |

---

## 四、N8N 自动化方案

### 4.1 部署

```bash
# docker-compose 中 n8n 服务，或单独：
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```

控制台：<http://localhost:5678>

### 4.2 工作流：文章发布通知（必做）

```mermaid
sequenceDiagram
  participant User as 用户
  participant API as FastAPI
  participant N8N as N8N
  participant Mail as 邮件或Webhook

  User->>API: POST /posts publish
  API->>API: 写入 MySQL
  API->>N8N: POST Webhook payload
  N8N->>Mail: 发送通知
  API->>User: 返回成功
```

**Webhook payload 示例：**

```json
{
  "event": "post.published",
  "post_id": 42,
  "title": "FastAPI 接入 Dify 复盘",
  "url": "https://yourdomain.com/content/42",
  "author": "cyinc",
  "published_at": "2026-07-05T10:00:00+08:00"
}
```

N8N 节点链：`Webhook` → `Set`（格式化）→ `Send Email` 或 `HTTP Request`（推企业微信/Bark 等）

### 4.3 FastAPI 触发方式

```python
# 文章 status 变为 published 后
await n8n_client.trigger_webhook("post-published", payload)
```

失败不阻塞发布（异步 fire-and-forget + 日志）。

### 4.4 环境变量

```env
N8N_WEBHOOK_URL=http://127.0.0.1:5678/webhook/post-published
N8N_WEBHOOK_SECRET=optional-shared-secret
```

---

## 五、Docker Compose 本地全家桶

根目录 `docker-compose.yml`（Phase A 必做）：

| 服务 | 端口 | 说明 |
|------|------|------|
| mysql | 3306 | 业务库 `cyinc` |
| redis | 6379 | 缓存 |
| dify | 3000 / 5001 | Dify 控制台 / API（按官方 compose） |
| n8n | 5678 | 工作流 |
| backend | 8000 | FastAPI（可选容器化，也可宿主机跑） |

**日常开发两种方式：**

1. **轻量**：phpstudy MySQL + Docker 只跑 redis/dify/n8n  
2. **标准**：`docker compose up -d` 全家桶，贴近生产

`docker-compose.yml` 与 `deploy/` 目录一并维护，README 写清两种模式。

---

## 六、Phase 任务分解

### Phase A — 必做（对齐 JD + 简历核心）

#### A1 FastAPI 后端基础

- [x] 脚手架 + 注册 / 登录 / JWT（M1 已完成）
- [x] 用户资料 GET/PATCH（`/users/me`）
- [x] 文章 CRUD（M2 已完成）
- [x] 番茄钟 sessions + stats
- [x] Redis 缓存 `GET /posts` 列表（无 Redis 时跳过缓存）

#### A2 Dify 自建 + AI 功能

- [ ] Docker 部署 Dify，配置 LLM 提供商（通义等）→ 见 `deploy/README-dify.md`
- [ ] 创建「文章摘要」Workflow，拿到 API Key
- [ ] 创建「站内助手」Chatflow + 知识库（导入部分博客）
- [x] FastAPI `dify_client.py` + `/api/v1/ai/summary`、`/api/v1/ai/chat`、`/posts/{id}/summary`
- [x] 前端：`/ai` 聊天页 + NavBar 入口

**验收**：Swagger 或前端完成「发文 → 生成摘要 → AI 助手回答站点相关问题」。

#### A3 N8N 发布自动化

- [ ] Docker 部署 N8N
- [ ] 配置 `post-published` Webhook 工作流
- [ ] FastAPI 发布文章后触发 Webhook
- [ ] 通知到达（邮件 / 控制台日志均可）

**验收**：发布一篇文章 → N8N 执行记录成功 → 收到通知。

#### A3 N8N 发布自动化

- [ ] n8n.io 注册，创建 `post-published` Webhook 工作流
- [x] FastAPI 发布文章后触发 Webhook（`n8n_client.py`）
- [ ] 在 n8n Executions 里看到记录即验收

#### A4 Redis / Docker（方案 A 跳过）

- [x] `docker-compose.yml` 保留供 M6 使用
- [x] 无 Redis 时 API 自动降级
- [ ] **M6 ECS** 再启用 Redis + Docker Compose

#### A5 前端 Hub + 个人中心 + 番茄钟

- [x] Hub 入口 `/hub`（M5）→ **M5.5 重定向 `/app`**
- [x] **PlatformLayout + PlatformNav** 主站壳
- [x] `/app/me` 个人中心 v2（四 Tab + 专注时间线）
- [x] `/app/pomo` 番茄钟 v2（圆环 / 设置 / 全屏 / 通知 / 反思）
- [x] `/app/forum` 论坛 MVP（三板块 + 发帖回帖）
- [x] 博客 NavBar「主站」↔ PlatformNav「返回博客」

#### A6 博客双轨 + 阿里云部署

- [ ] 新文走 API；旧静态文只读
- [ ] ECS + Nginx + HTTPS + systemd
- [ ] Dify/N8N 同机 Docker 或分机部署
- [ ] 复盘文章 1～2 篇（Dify 接入、N8N 自动化、ECS 部署）

---

### Phase B — 面试加分（上线后）

- [ ] GitHub Actions SSH 部署到 ECS
- [ ] pytest + 前端 vitest
- [ ] Dify 知识库全量同步博客脚本
- [ ] refresh token / httpOnly cookie
- [ ] 阿里云 DMS 管理生产 MySQL

---

### Phase C — 暂不做 / 低优先级

- 论坛管理员删帖/置顶 UI
- Markdown 渲染器（MVP 纯文本换行）
- 子域名拆分（`blog.xxx` / `forum.xxx`，M6）
- 微服务拆分

---

## 七、仓库目录结构

```
gerenboke/
├── src/                          # Vue 前端
│   └── views/
│       ├── Hub.vue               # 新增
│       ├── AiChat.vue            # 新增：Dify 助手
│       └── ...
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth.py           # M1 已有
│   │   │   ├── posts.py
│   │   │   ├── pomodoro.py
│   │   │   └── ai.py             # Dify 代理
│   │   ├── services/
│   │   │   ├── dify_client.py
│   │   │   ├── n8n_client.py
│   │   │   └── redis_cache.py
│   │   └── ...
│   └── requirements.txt
├── docker-compose.yml            # mysql + redis + n8n (+ dify 说明)
├── deploy/
│   ├── nginx.conf.example
│   ├── cyinc-api.service.example
│   └── dify-nginx-snippet.example
├── 笔记/项目/
│   └── CYINC动态主站工作流.md
└── README.md
```

---

## 八、API 设计概要

前缀：`/api/v1`

### 鉴权（M1 已有）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/register` | 注册 |
| POST | `/auth/login` | 登录 |
| GET | `/auth/me` | 当前用户 |

### 文章

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/posts` | 列表（Redis 缓存） |
| GET | `/posts/{id}` | 详情 |
| POST | `/posts` | 创建 |
| PATCH | `/posts/{id}` | 更新 |
| DELETE | `/posts/{id}` | 删除 |
| POST | `/posts/{id}/summary` | 调 Dify 生成/刷新摘要 |

### AI（Dify 代理）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/ai/chat` | 站内助手对话（转发 Dify Chatflow） |
| POST | `/ai/summary` | 传入正文，返回摘要（转发 Dify Workflow） |

### 番茄钟

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/pomodoro/sessions` | 记录专注（含可选 `reflection`） |
| GET | `/pomodoro/sessions` | 我的记录 |
| GET | `/pomodoro/stats` | 统计 |
| GET | `/pomodoro/timeline` | 按日分组时间线（个人中心） |

### 论坛（M5.5）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/forum/categories` | 板块列表 |
| GET | `/forum/categories/{slug}/threads` | 板块内帖子 |
| GET | `/forum/threads/recent` | 最新帖子 |
| GET | `/forum/threads/mine` | 我的帖子 |
| GET | `/forum/threads/{id}` | 帖子详情 + 回帖 |
| POST | `/forum/threads` | 发帖（登录） |
| POST | `/forum/threads/{id}/replies` | 回帖（登录） |

---

## 九、数据库表设计

### users / posts / pomodoro_sessions / forum_*

（`pomodoro_sessions` 含 `reflection`；论坛三表见 M5.5，启动时 seed 三板块）

### ai_chat_logs（可选，Phase B）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | |
| user_id | BIGINT FK NULL | 未登录可为空 |
| query | TEXT | 用户问题 |
| answer | TEXT | Dify 回复 |
| created_at | DATETIME | |

---

## 十、本地开发与环境变量

### 10.1 前置依赖

- Node.js 20+、Python 3.11+
- Docker Desktop（跑 Redis / Dify / N8N）
- MySQL：phpstudy **或** docker-compose 中的 mysql

### 10.2 推荐启动顺序

```bash
# 1. 基础设施
docker compose up -d mysql redis n8n
# Dify 见 deploy/README-dify.md 或官方 docker/

# 2. 后端
cd backend && copy .env.example .env
uvicorn app.main:app --reload --port 8000

# 3. 前端
npm run dev
```

### 10.3 backend/.env 完整示例

```env
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/cyinc
SECRET_KEY=change-me-in-production
REDIS_URL=redis://127.0.0.1:6379/0

DIFY_API_URL=http://127.0.0.1:5001
DIFY_SUMMARY_API_KEY=app-xxx
DIFY_CHAT_API_KEY=app-yyy
DIFY_TIMEOUT_SEC=30

N8N_WEBHOOK_URL=http://127.0.0.1:5678/webhook/post-published

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 10.4 联调检查清单

- [ ] MySQL `cyinc` 库已建，FastAPI 启动无报错
- [ ] Redis `PING` 通
- [ ] Dify 控制台可登录，Workflow 测试 Run 成功
- [ ] N8N Webhook 测试触发成功
- [ ] Swagger `/api/docs` 全流程
- [ ] 前端 `/ai` 页面对话有回复

---

## 十一、阿里云部署 Checklist

在 v1.0 基础上增加：

### 11.1 ECS 资源

- [ ] ECS 建议 **4C8G**（跑 Dify 比纯 API 更吃内存；预算紧可 Dify 放第二台或本地演示 + 生产只部署 API）
- [ ] 安全组：80/443/22；Dify/N8N **不暴露公网**，仅 127.0.0.1 或内网
- [ ] RDS MySQL 或自建 MySQL
- [ ] Redis：阿里云 Redis 版或 ECS Docker

### 11.2 服务布局（单机 MVP）

| 组件 | 方式 |
|------|------|
| Nginx | 系统包，反代 `/` `/api` |
| FastAPI | systemd + venv |
| Dify | Docker Compose |
| N8N | Docker |
| Redis | Docker 或阿里云 Redis |
| MySQL | RDS |

### 11.3 Nginx 补充（Dify 内网时可省略公网反代）

业务 API 与静态站同 v1.0；Dify 仅 `127.0.0.1:5001` 供 FastAPI 调用。

### 11.4 冒烟测试

- [ ] 全站 HTTPS
- [ ] 注册 → 发文 → AI 摘要 → N8N 通知
- [ ] `/ai` 助手在线
- [ ] Redis 缓存命中（可打日志验证）

---

## 十二、Git 分支与里程碑

### 12.1 分支

| 分支 | 用途 |
|------|------|
| `main` | 稳定 |
| `feat/platform-v2-fastapi` | Phase A 全部（当前） |

### 12.2 里程碑（按 JD 重排）

| 序号 | 内容 | 状态 | 对应 JD |
|------|------|------|---------|
| M1 | FastAPI 注册登录 JWT | **已完成** | Python |
| M2 | Post CRUD + Redis 缓存 | **已完成** | MySQL + Redis |
| M3 | Dify Cloud + `/ai` | **代码完成**（待填 Cloud Key） | **Dify LLMOps** |
| M4 | n8n Cloud Webhook | **代码完成**（待填 Webhook URL） | **N8N 自动化** |
| M5 | Hub + `/me` + 番茄钟 | **已完成** | Vue |
| M5.5 | 主站分离 + 论坛 MVP + 番茄钟 v2 | **已完成** | Vue + FastAPI |
| M6 | ECS 整站同域上线 | **方案已定**（见 `deploy/README-m6-ecs.md`） | 部署 + Docker |
| M7 | 复盘文章 + 简历 | 待做 | Cursor 协作过程 |

---

## 十三、求职交付物清单

1. **GitHub README** — 架构图含 Dify/N8N/Redis/Docker
2. **Swagger** — `https://域名/api/docs`
3. **Dify** — 控制台截图 + Workflow 设计说明（可放博客）
4. **N8N** — 工作流导出 JSON 放 `deploy/n8n/`
5. **docker-compose** — 一条命令起环境
6. **projects.js** — CYINC Platform v2 条目
7. **复盘文** — 《FastAPI 接入自建 Dify》《N8N 发文自动化》（优先于论坛）
8. **简历 bullet** — 见附录 A

---

## 附录 A · 简历项目描述（对齐 JD 版）

**CYINC 个人 AI 工作平台** | Vue 3 · FastAPI · MySQL · Redis · Dify · N8N · Docker · 阿里云 ECS  
*2026.06 – 至今*

- 使用 **Cursor** 协作完成 Vue 3 + FastAPI 前后端分离开发，JWT 鉴权、文章 CRUD、OpenAPI 文档化接口与 **Redis** 列表缓存。
- **自建 Dify**（Docker），编排文章摘要 Workflow 与站内 RAG 助手 Chatflow，FastAPI 统一封装调用与超时降级。
- 使用 **N8N** 搭建「发文 → Webhook → 通知」自动化链路；**Docker Compose** 编排 MySQL/Redis/Dify/N8N 本地环境。
- **Nginx** + Uvicorn + systemd 部署于 **阿里云 ECS**，HTTPS 上线；复盘文记录 LLMOps 接入与部署过程。

**补充项目**：陈皮有多陈（Flask + 通义千问视觉鉴定）— 体现 Python AI 基础，对比升级为 Dify 工作流编排。

---

## 附录 B · 面试话术（含 Dify / N8N）

| 问题 | 回答要点 |
|------|----------|
| 为什么 Dify 自建不用 Coze？ | 需要 API 层控制、Docker 部署、与 FastAPI 深度集成；Coze 偏 SaaS 零代码 |
| Dify 怎么和 FastAPI 分工？ | Dify 管 Prompt/工作流/知识库；FastAPI 管鉴权、业务数据、统一降级 |
| Workflow 和 Chatflow 区别？ | Workflow 单次输入输出（摘要）；Chatflow 多轮对话 + RAG（助手） |
| N8N 和 GitHub Actions 区别？ | Actions 偏 CI/CD；N8N 偏业务事件编排（发文通知、多系统集成） |
| AI 调用失败怎么办？ | 超时返回友好提示，摘要字段为空不阻塞发文 |
| Redis 用在哪？ | 文章列表缓存、可选 API 限流 |
| Docker Compose 包含什么？ | mysql、redis、n8n；Dify 用官方 compose，文档说明如何并联 |

---

## 附录 C · Phase A 范围确认

- [x] 技术栈：FastAPI + MySQL + Redis + **Dify 自建** + **N8N** + Docker + 阿里云 ECS/Nginx
- [x] AI：**不用 Coze**，Dify Workflow + Chatflow
- [x] Phase A：鉴权 + CRUD + Dify + N8N + Docker + Hub + 番茄钟 + ECS
- [x] 论坛：M5.5 MVP 已完成（管理员 UI 留 Phase C）
- [x] 分支：`feat/platform-v2-fastapi`
- [x] M1 后端脚手架：已完成
- [ ] 生产域名：____________

**确认人**：________  
**确认日期**：________

---

*文档维护：v2.0 起每完成 Milestone 更新 §12.2 状态列与 Phase 任务 checkbox。*
