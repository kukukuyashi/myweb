---
title: "线上笔记管理台：/myweb/admin"
date: "2026-07-15"
category: "部署"
tags: ["部署", "Admin", "笔记", "FastAPI", "ECS"]
excerpt: "生产环境笔记管理台：用运维账号登录 /myweb/admin，编辑 Markdown 并发布到 Content + posts.json，与 SQLAdmin /admin 分工。"
cover: "img/bgm/2.jfif"
---

# 线上笔记管理台：/myweb/admin

> 与本地 `npm run dev` 时的笔记台类似，但生产走 **FastAPI `/api/v1/notes-admin`**，有登录鉴权。

## 两个后台别混

| 入口 | 作用 |
|------|------|
| `https://域名/admin` | SQLAdmin：用户、论坛帖、API 动态文章等**数据库** |
| `https://域名/myweb/admin` | 笔记管理台：`笔记/*.md` → 博客 `Content/*.html` + `data/posts.json` |

登录口令同一套：`ADMIN_USERNAME` + `ADMIN_PASSWORD_HASH`。

## 发布后落盘

- Markdown：`/var/www/cyinc/笔记`（容器 `/data/notes`）
- 正文：`/var/www/cyinc/myweb/Content/`
- 目录：`/var/www/cyinc/myweb/data/posts.json`（首页运行时优先读它，不必立刻 `npm run build`）

## ECS 注意

1. `backend/.env` 设置 `NOTES_ROOT=/data/notes`、`SITE_WEB_ROOT=/data/web`
2. `docker-compose.prod.yml` 已挂载 `./笔记`、`./myweb`
3. 部署脚本会 `mkdir` 对应目录；首次可 rsync 本机 `笔记/` 与构建产物中的 `data/posts.json`

## 验收

- 未登录不能调用写接口（401）
- 登录 → 新建 → 保存 → 发布 → `/myweb/` 列表出现 → `/myweb/content/{id}` 可读

相关：[deploy/README-m6-ecs.md](../../deploy/README-m6-ecs.md) §3.8
