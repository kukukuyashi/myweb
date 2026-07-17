---
title: "ECS 生产排障：论坛 Token 无效与登录 502"
date: "2026-07-14"
category: "部署"
tags: ["部署", "Docker", "JWT", "Nginx", "FastAPI", "ECS"]
excerpt: "线上论坛提示 token 无效、登录页 502 Bad Gateway 的一次完整复盘：从请求链路讲清 JWT、Nginx、Docker、MySQL 与 .env，附专有名词解释与排障清单。"
cover: "img/bgm/2.jfif"
---

# ECS 生产排障：论坛 Token 无效与登录 502

> 写于 2026-07-14 · CYINC 全栈站上线阿里云 ECS 后的真实故障复盘  
> 适用场景：`http://你的ECS_IP/myweb/` 论坛发帖失败、登录页报 502，本机开发却正常。

---

## 一、这次发生了什么（用大白话说）

网站分成两层：

1. **前端页面**（Vue 打包后的 HTML/JS）—— 浏览器里看到的登录按钮、论坛页面  
2. **后端 API**（FastAPI，跑在 Docker 里）—— 真负责「登录验身份」「存帖子」的服务  

用户会遇到两种表面现象，其实是**同一条生产链路上的两个症状**：

| 现象 | 用户看到的字 | 实际含义 |
|------|--------------|----------|
| A | 论坛提示 **token 无效** | 浏览器带着「旧通行证」去访问 API，API 验不过 |
| B | 登录页 **502 (Bad Gateway)** | Nginx 还活着，但后面的 API 容器已经挂了，登录请求根本到不了后端 |

可以把它想成：

- **502** = 银行柜台的「窗口大门」还开着（Nginx），但柜员不在岗（API 挂了）  
- **token 无效** = 你拿着昨天的门票，换了一把锁的门卫（新的密钥）验不过；或服务恢复后，旧票本就该作废  

---

## 二、请求是怎么走的（整站同域架构）

生产大致链路（ECS 上）：

```text
浏览器
  │  访问 http://ECS_IP/myweb/app/login 或 /myweb/app/forum
  ▼
Nginx（80 端口）
  ├─ /myweb/     → 静态前端文件（/var/www/cyinc/myweb/）
  ├─ /api/       → 反代到 127.0.0.1:8000（FastAPI 容器）
  └─ /admin/     → 同样反代到 FastAPI（SQLAdmin 后台）
         │
         ▼
FastAPI 容器（cyinc_api_1）
  ├─ 连 MySQL（业务用户、论坛帖子）
  └─ 连 Redis（缓存、验证码等）
```

**同域**：页面和 API 都在同一个主机（同一 IP/域名）下，前端用相对路径 `/api/v1`，浏览器不会跨到别的网站去请求。

若构建前端时误把 API 地址写死成 `http://127.0.0.1:8000`，浏览器会去连**访问者自己电脑**上的 8000 端口——那会变成「Failed to fetch / CONNECTION_REFUSED」，那是另一类坑，本文重点是 token 与 502。

---

## 三、现象 A：论坛「token 无效」

### 3.1 专有名词：什么是 Token？

**Token（令牌）**：登录成功后，服务器发给浏览器的一串加密字符串，相当于「临时通行证」。

之后发帖、回帖、改资料时，浏览器会在请求头里带上：

```http
Authorization: Bearer <你的token>
```

服务器验一下这串票是否合法，合法才放行。

本站前端把 token 存在浏览器的 **localStorage**（本地存储）：

- 键名：`cyinc_platform_token`
- 代码：`src/api/platform.js` 的 `getPlatformToken()` / `setPlatformToken()`

**localStorage**：浏览器提供的「网站专属小仓库」。关标签页不会丢，换设备/无痕窗口就没有。同一域名（或同源策略下的同一站）共享这份数据。

### 3.2 专有名词：什么是 JWT？

本站用的是 **JWT（JSON Web Token）**：一种常见的 Token 格式。

它大致分三段用点连起来：`xxxxx.yyyyy.zzzzz`

1. **Header（头）**：说明用什么算法签名  
2. **Payload（载荷）**：放用户名（`sub`）、过期时间（`exp`）等  
3. **Signature（签名）**：用服务器的 **SECRET_KEY（密钥）** 算出来的防伪码  

服务器校验时：

```text
用当前 SECRET_KEY 重新算签名
  → 对得上 + 没过期 → 有效
  → 对不上或过期 → 返回「token 无效」
```

对应后端代码：`backend/app/api/deps.py`  
报错原文：`detail="token 无效"`（HTTP **401 Unauthorized**）。

**401**：未授权——你不是没连上服务器，而是「身份不被接受」。  
**403**：禁止——常常是鉴权过了但不让你做这件事（本文备案拦截有时也是 403）。

### 3.3 SECRET_KEY 是什么？为什么本地和线上不一样？

**SECRET_KEY**：写在服务器环境变量 `.env` 里的一长串密钥，**只存在服务器，不要提交到 Git**。

JWT 的签名依赖它：

```
本机 backend/.env 的 SECRET_KEY  ≠  ECS 上 backend/.env 的 SECRET_KEY
```

所以会发生：

1. 你以前在 **本机** 登录过 → 浏览器 `localStorage` 里留下本机签发的 token  
2. 后来打开 **线上** `http://ECS_IP/myweb/` → 同源不同、或换过密钥后，旧票失效  
3. 论坛发帖带上旧 token → API 验签失败 → **token 无效**

也可能：

- ECS 上重新生成过 `SECRET_KEY`、改过 `.env`、重建过容器注入了新密钥  
- Token **过期**了（本项目默认大约 7 天，`ACCESS_TOKEN_EXPIRE_MINUTES`）

### 3.4 为什么清一下再登录就好？

因为合法做法只有一条：**向当前这台正在运行的 API，用正确密钥重新登录**，拿到新 token。

浏览器控制台可执行：

```js
localStorage.removeItem('cyinc_platform_token')
location.reload()
```

然后打开登录页重新登录。  
注意：若此时 API 已经是 **502**，登录会失败——必须先把 API 拉起来（见下一节）。

---

## 四、现象 B：登录 502 Bad Gateway

### 4.1 专有名词：什么是 502？

**502 Bad Gateway**：网关（这里是 **Nginx**）作为「前台接待」，转发给「后台服务员（FastAPI）」时，**后台没响应或连接失败**。

不等于「密码错了」：

| 状态 | 含义 |
|------|------|
| 200 | 成功 |
| 401 | 通了后端，但身份不对（如 token 无效、密码错） |
| 403 | 禁止访问（如域名未备案被阿里云拦截） |
| **502** | **后端进程/容器挂了，Nginx 交不出话** |

可以用这个区分：

```bash
# 在 ECS 上：绕过 Nginx，直连接口
curl -s http://127.0.0.1:8000/api/health

# 走 Nginx
curl -s http://127.0.0.1/api/health
```

- 前者失败 → API 容器或进程挂了  
- 前者成功、后者 502 → Nginx 配置/上游地址有问题（本次故障少见）  
- 两者都返回 `{"status":"ok"...}` → API 正常  

### 4.2 专有名词：Nginx / 反代 / Upstream

- **Nginx**：高性能 Web 服务器，这里负责：
  - 托管 Vue 静态文件（`/myweb/`）
  - **反向代理（Reverse Proxy）**：把 `/api`、`/admin` 转发给内部的 FastAPI  
- **Upstream**：Nginx 配置里写的「后端目标」，例如 `127.0.0.1:8000`  
- **127.0.0.1**：本机回环地址，只在服务器内部访问，不对公网直接暴露 8000（更安全）

### 4.3 这次 API 为什么挂了？

多次复现后，主因集中在 **Docker 容器里连不上宿主机 MySQL**。

日志里典型错误类似：

```text
Can't connect to MySQL server on 'host.docker.internal'
# 或 Name or service not known
```

API 容器进 `Restarting` 循环 → 8000 没服务 → Nginx → **502**。

---

## 五、Docker、MySQL、网络：这次最容易踩的坑

### 5.1 专有名词：Docker / 容器 / 镜像

| 名词 | 通俗解释 |
|------|----------|
| **镜像（Image）** | 软件安装包模板，如 `cyinc_api:latest` |
| **容器（Container）** | 按镜像跑起来的实例，如 `cyinc_api_1` |
| **Docker Compose** | 用一份 YAML（如 `docker-compose.prod.yml`）一键管理多个容器 |
| **网络（Network）** | 容器之间的虚拟局域网；本站 Redis 在 `cyinc_default` |
| **Volume（卷）** | 容器删了数据还在的小硬盘分区，如头像上传目录 |

本站生产常见容器：

- `cyinc_api_1`：FastAPI  
- `cyinc_redis_1`：Redis  

MySQL 则装在 **ECS 宿主机**（非容器），用 systemd：`systemctl status mysql`。

### 5.2 专有名词：宿主机 / Docker 网关 / host.docker.internal

| 名词 | 含义 |
|------|------|
| **宿主机（Host）** | 跑 Docker 的那台 Linux（你的阿里云 ECS） |
| **容器内的 localhost** | 指容器自己，**不是**宿主机 |
| **host.docker.internal** | Docker Desktop（Windows/Mac）常用的「指向宿主机」主机名 |
| **172.17.0.1** | Linux 上 Docker 默认网桥 `docker0` 的网关 IP，常用来从容器访问宿主机 |

**坑点：**  

在 **Linux ECS** 上，`host.docker.internal` **默认不一定存在**。  
`.env` 若写成：

```env
DATABASE_URL=mysql+pymysql://用户:密码@host.docker.internal:3306/库名
```

容器可能解析失败 → 启动时连库崩溃 → Restarting → **502**。

**正确做法（本机 MySQL 方案）：**

```env
DATABASE_URL=mysql+pymysql://用户:密码@172.17.0.1:3306/库名
```

同时 MySQL 要允许 Docker 访问，例如：

```text
bind-address = 0.0.0.0
```

（并给 `cyinc@'%'` 这类用户授权，勿把 3306 安全组对整个公网敞开。）

### 5.3 专有名词：--link 与 Docker 网络

曾经用过：

```bash
docker run ... --link cyinc_redis_1:redis ...
```

若 Redis 是 **docker compose** 建在 `cyinc_default` 网络上，而默认 bridge 上没有它，会报错类似：

```text
container ... not attached to default bridge network
```

API **创建失败** → 当然还是 502。

**正确做法：** 让 API 加入 Redis 同一网络：

```bash
docker run -d --name cyinc_api_1 \
  --network cyinc_default \
  --env-file backend/.env \
  -e REDIS_URL=redis://redis:6379/0 \
  -p 127.0.0.1:8000:8000 \
  ...
```

- **`--network cyinc_default`**：进 compose 那张网，才能用主机名 `redis` 找到 Redis  
- **`-p 127.0.0.1:8000:8000`**：只在本机监听，给 Nginx 反代用  

### 5.4 专有名词：.env / --env-file / 为什么改了密码还不对

| 名词 | 含义 |
|------|------|
| **`.env`** | 环境变量文件，放数据库地址、SECRET_KEY、Admin 哈希等秘密配置 |
| **`--env-file`** | `docker run` 时把文件内容注入容器环境变量——**只在创建容器那一刻生效** |
| **`docker restart`** | 重启**同一个**容器：进程重启，但**环境变量仍是创建时那套** |

所以会出现：

1. 你改好了 `backend/.env` 里的 `ADMIN_PASSWORD_HASH`  
2. 执行了 `docker restart cyinc_api_1`  
3. Admin 登录仍「用户名或密码错误」  

因为容器里还是旧环境！必须：

```bash
docker rm -f cyinc_api_1
docker run ... --env-file backend/.env ...   # 重新创建
```

**Admin（SQLAdmin）密码** 存在 `ADMIN_PASSWORD_HASH`（bcrypt 哈希），**查不出明文**，只能重置。  
`Cyinc` / 数据库密码 和 Admin 账号 `admin` **不是同一套东西**。

---

## 六、两个现象如何连在一起理解

时间线常见是这样：

```text
1. API 因 MySQL 地址写错（host.docker.internal）进入 Restarting
2. 登录 → Nginx 502
3. （偶尔）API 曾短暂起来过，或你本机/旧环境留过 token
4. 论坛发帖带着旧 JWT → token 无效
5. 修好 DATABASE_URL + 网络 + 重建容器后 API healthy
6. 清 localStorage，重新登录 → 论坛恢复
```

所以：**先修 502（让 API 健康），再清 token 重登（消掉无效令牌）。**

---

## 七、完整排障清单（可收藏）

### 7.1 在 ECS 上一键自检

```bash
cd /var/www/cyinc

# MySQL
systemctl is-active mysql

# 数据库连接地址（应含 172.17.0.1，不应是未解析的 host.docker.internal）
grep DATABASE_URL backend/.env

# 容器状态
docker ps -a | grep cyinc

# API 健康
curl -s http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1/api/health

# 若 API 反复重启，看日志
docker logs cyinc_api_1 --tail=50
```

健康输出应类似：

```json
{"code":0,"message":"ok","data":{"status":"ok","service":"cyinc-api"}}
```

### 7.2 修复 API（摘要命令）

```bash
cd /var/www/cyinc

# 修正 MySQL 地址
sed -i 's/@host.docker.internal:3306/@172.17.0.1:3306/' backend/.env
sudo systemctl start mysql

# 重建 API（加入 compose 网络）
docker rm -f cyinc_api_1
docker run -d --name cyinc_api_1 \
  --network cyinc_default \
  --add-host=host.docker.internal:host-gateway \
  --env-file backend/.env \
  -e REDIS_URL=redis://redis:6379/0 \
  -p 127.0.0.1:8000:8000 \
  -v cyinc_uploads_data:/app/uploads \
  --restart unless-stopped \
  cyinc_api:latest

sleep 10
docker ps | grep cyinc_api
curl -s http://127.0.0.1:8000/api/health
```

### 7.3 浏览器收尾

1. 打开 `http://ECS_IP/myweb/app/login`  
2. F12 控制台：

```js
localStorage.removeItem('cyinc_platform_token')
location.reload()
```

3. 重新登录 → 再试论坛发帖  

### 7.4 重置 Admin 密码（概要）

1. 生成 bcrypt 哈希（明文密码仅你自己知道，不要写进仓库）  
2. 写入 `backend/.env` 的 `ADMIN_USERNAME` / `ADMIN_PASSWORD_HASH`  
3. **`docker rm` + `docker run --env-file`** 重建容器（不要只 restart）  
4. 访问 `/admin/login`，用新密码登录  

后台入口示例：`http://ECS_IP/admin/login`（SQLAdmin 数据管理）。

---

## 八、和「域名备案」别搞混

若访问域名出现阿里云「域名暂时无法访问」类提示：那是 **ICP 备案** 未通过时的拦截，状态码可能是 **403**，**不是** 本文的 502。

| 场景 | 表现 | 处理 |
|------|------|------|
| API 挂了 | IP 访问 `/api/health` 也是 502 | 修 Docker/MySQL |
| 未备案 | `域名` 被拦截；IP 往往还能用 | 等备案 / 用 IP 临时访问 |
| Token | 页面有提示「token 无效」 | 清 storage 重登；确认 SECRET_KEY 未突变 |

备案相关流程见部署文档 `deploy/DEPLOY-PLAN.md`、`deploy/README-m6-ecs.md`。

---

## 九、专有名词速查表

| 名词 | 一句话解释 |
|------|------------|
| **ECS** | 云服务器，一台可 SSH 登录的远程 Linux |
| **Nginx** | 对外提供网页、并把 /api 转给后端的网关 |
| **FastAPI** | Python Web 框架，本站后端 API |
| **SQLAdmin** | 基于 FastAPI 的数据管理后台（`/admin`） |
| **JWT / Token** | 登录后的加密通行证 |
| **SECRET_KEY** | 签发/校验 JWT 的密钥，环境间不能混用 |
| **localStorage** | 浏览器本地存 token 的地方 |
| **401** | 身份校验失败 |
| **502** | 网关背后没有可用的后端 |
| **Docker 容器** | 隔离运行后端服务的「小箱子」 |
| **宿主机** | 跑着 Docker 的那台 ECS |
| **172.17.0.1** | 容器访问宿主机 MySQL 的常用网关 IP |
| **host.docker.internal** | 桌面版 Docker 指宿主机；Linux 上常不可用 |
| **.env / --env-file** | 环境变量；改文件后通常需重建容器 |
| **Redis** | 内存数据库，做缓存/验证码等 |
| **bcrypt 哈希** | 不可逆的密码摘要，只能验证不能还原明文 |
| **反向代理** | Nginx 替浏览器去问内部 API，再把结果返回 |
| **同域部署** | 前端与 API 共用同一主机名，减少跨域问题 |

---

## 十、以后如何少踩坑（实践建议）

1. **生产 `.env` 只放 ECS 上**，DATABASE 用 `172.17.0.1`（本机 MySQL 方案）或 RDS 内网地址  
2. **改 `.env` 后务必重建容器**（`rm` + `run` 或 `docker compose up -d --force-recreate`），别只 `restart`  
3. **前端生产构建**必须带：`VITE_API_BASE_URL=/api/v1`（相对路径），禁止打进 `127.0.0.1:8000`  
4. **1.6G～2G 内存** ECS 建议加 Swap，避免 MySQL/API 被 OOM Kill  
5. 服务器重启后检查：`mysql` 是否 active、`docker ps` 是否 healthy、`curl /api/health`  
6. **不要把生产密码、SECRET_KEY、Admin 哈希贴到公开仓库或聊天截图**；泄露后及时轮换  

---

## 十一、本次复盘结论

| 问题 | 根因 | 解法 |
|------|------|------|
| 登录 502 | API 容器连不上 MySQL / 网络起容器失败 | 改 `172.17.0.1`、同一 Docker 网络重建 API |
| token 无效 | JWT 与当前 `SECRET_KEY` 不一致，或过期 | 清 `cyinc_platform_token`，API 健康后重登 |
| Admin 改了哈希仍登不上 | `restart` 未重新加载 `--env-file` | 删容器并用 `--env-file` 重建 |

一句话记住：

> **502 先看后端活没活；token 无效先看是不是旧票、有没有换过门锁（SECRET_KEY）。改 `.env` 一定要重建容器，不是重启一下就完事。**

---

## 十二、相关代码与文档

| 路径 | 内容 |
|------|------|
| `backend/app/api/deps.py` | JWT 校验，抛出「token 无效」 |
| `backend/app/core/security.py` | 签发 JWT |
| `src/api/platform.js` | 前端存取 token、请求 API |
| `backend/app/admin/auth.py` | SQLAdmin 登录校验 |
| `docker-compose.prod.yml` | 生产编排（建议含 `extra_hosts`） |
| `deploy/DEPLOY-PLAN.md` | ECS 部署与日常更新清单 |
| `deploy/README-m6-ecs.md` | M6 整站上线说明 |

---

*本文记录的是一次真实生产排障过程，文中命令为操作示例；密码与密钥请使用你自己环境中的值，勿照抄聊天记录中的明文。*
