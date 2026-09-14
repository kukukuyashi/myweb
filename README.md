# CYINC.LOG

Cyinc 的个人全栈站点 — 静态博客 + 动态平台，同域部署在阿里云 ECS。

- 生产环境：<https://cyinc.ink/myweb/>
- GitHub Pages（备用静态形态）：<https://kukukuyashi.github.io/myweb/>

## 这是什么

仓库名 `gerenboke`，包含两部分：

1. **博客主站**（Vue 3 + Vite）：文章、归档、项目、音乐室、留言板、关于页。构建产物在 `docs/`，线上由 Nginx 以 `/myweb/` 提供。
2. **动态平台**（同仓 FastAPI + MySQL + Redis）：用户体系与互动功能，入口 `/myweb/app/*`，管理台 `/myweb/admin/*`。

## 功能概览

**博客**

- 首页：分类 / 标签 / 搜索、系列导航、精选文章
- 文章：目录、阅读进度、代码高亮、Twikoo 评论、复制链接、JSON-LD
- 归档：时间轴 + 月份热力预览；标签页 `/tags/:tag` 独立 URL
- 音乐室、留言板、关于页（贴纸墙 + 墨染交互）、项目卡片墙、更新日志
- 构建期 prerender：文章 / 标签 / 主要页面静态 HTML（SEO），自动生成 RSS / sitemap / robots.txt

**平台 `/app/*`**

- 注册 / 登录（JWT）、个人资料、头像上传
- 用户文章（编辑器 + 详情页）、论坛（板块 / 发帖 / 回帖 / 点赞）、留言板 Q&A
- 番茄钟与专注空间、签到与 XP、聊天室（WebSocket）
- 番剧放送表、街机小游戏、友情链接、AI 助手（Dify）
- 管理台：仪表盘 / 笔记 / 机器人 / 数据管理；SQLAdmin `/admin` 运维入口
- ACG 资讯机器人（APScheduler 定时任务）

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 · Vite 7 · Vue Router · Pinia · Prism.js · marked · DOMPurify |
| 后端 | FastAPI · SQLAlchemy 2 · PyMySQL · JWT · bcrypt · SQLAdmin · APScheduler |
| 数据 | MySQL（必需）· Redis（缓存 / 聊天室广播，可选降级） |
| 集成 | Dify Cloud（AI）· n8n（发文 Webhook）· Twikoo（博客评论） |
| 生产 | 阿里云 ECS · Docker · Nginx · HTTPS · Cloudflare R2（音乐 CDN） |

## 目录结构

```
src/                前端源码（views/platform/ 为 /app/* 平台页）
  api/              platform.js 等 → 调 /api/v1
  data/             posts.js · series.js · projects.js · changelog.js · profile.js
笔记/               博客文章 Markdown 源文件（不入库产物见下）
Content/            发布生成的文章 HTML
docs/               vite build 输出（勿手改）
backend/app/        FastAPI：api/v1 · models · schemas · services · admin · core
scripts/            构建、发文、缩略图、音乐 CDN 上传等脚本
deploy/             ECS 部署文档与 Nginx / systemd 示例
img/  Music/        媒体资源（大图库与音乐不随 Git 全量同步，生产由 Nginx/R2 提供）
```

## 本地开发

```bash
# 前端（base 与生产一致）
npm install
npm run dev          # http://localhost:5173/myweb/

# 后端（需先启动 MySQL，详见 backend/README.md）
npm run dev:api      # http://127.0.0.1:8000 · /api/docs · /admin
```

前端联调在 `.env` 中设置 `VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1`。

## 发布一篇博客文章

```bash
npm run new:post        # 在 笔记/ 下脚手架新建 md
npm run publish:post    # md → Content/*.html，并更新 src/data/posts.js
npm run build           # 重新构建 docs/
```

可选元数据：系列归 `src/data/series.js`，项目复盘归 `src/data/projects.js`，站点更新归 `src/data/changelog.js`。

## 构建与部署

```bash
npm run build      # 导出 posts.json + 缩略图 + vite build → docs/ + feed/sitemap/prerender
npm run preview    # 本地预览构建产物
```

**生产部署**：ECS 上运行时数据（`site-data/` 的 posts.json 与文章 HTML）与前端产物物理隔离，部署有固定脚本与铁律，见：

- [deploy/README-m6-ecs.md](deploy/README-m6-ecs.md) — 整站 ECS 部署指南
- [deploy/nginx.conf.example](deploy/nginx.conf.example) — Nginx 配置（HTTP/2、缓存策略、反向代理）
- [backend/README.md](backend/README.md) — 后端建库、启动、SQLAdmin、API 一览、冒烟测试
- [AGENTS.md](AGENTS.md) — 部署铁律与协作者须知

性能要点：带 hash 的前端资源 `immutable` 长缓存、文章数据走 ETag/304 协商缓存、装饰图使用 WebP 缩略图、音乐走 R2 CDN 不占用 ECS 带宽。

## 环境变量

复制 `.env.example` 为 `.env.local`（不提交），按需配置：Twikoo `envId`、音乐 CDN `VITE_MUSIC_BASE_URL`、API Base，以及 `npm run music:upload` 用的 `CDN_S3_*` 对象存储凭据。后端变量见 `backend/.env.example` 与 `.env.production.example`。

## License

MIT（站点内容与图片除外，版权归作者所有）
