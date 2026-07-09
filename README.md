# CYINC.LOG · 个人博客

Cyinc 的技术学习日志 — Vue 3 静态博客，部署在 GitHub Pages。

在线地址：<https://kukukuyashi.github.io/myweb/>

## 功能概览

- 首页：分类 / 标签 / 搜索、系列导航、精选文章
- 文章：目录、阅读进度、代码高亮、Twikoo 评论、复制链接、JSON-LD
- 归档：时间轴 + 月份热力预览
- 项目：实战项目卡片墙
- 更新日志：站点功能演化时间线
- 标签页：`/tags/:tag` 独立 URL
- 构建 prerender：文章 / 标签 / 主要页面静态 HTML（SEO）
- 音乐室、留言板、关于页（贴纸墙 + 墨染交互）
- RSS / sitemap / robots.txt（build 时自动生成）

## 本地开发

```bash
npm install
npm run dev
```

默认 dev 地址：`http://localhost:5173/myweb/`（与生产 base 一致）

## 发布新文章

1. 在 `Content/` 放入 HTML 正文
2. 在 `src/data/posts.js` 的 `posts` 数组顶部加一条（`id` 递增、`file` 对应文件名）
   - 可选 `cover: 'img/...'` 作为分享预览图与卡片缩略图
3. 若属于某系列，在 `src/data/series.js` 的 `postIds` 里补上 id
4. 若是项目复盘，在 `src/data/projects.js` 加一条（可选）
5. 若是站点功能更新，在 `src/data/changelog.js` 加一条（可选）
6. 执行 `npm run build` 并 push

## 构建与部署

```bash
npm run build
```

产物输出到 `docs/`，并自动生成 feed、sitemap、**prerender 静态页**（供搜索引擎抓取正文）。

本地预览 build：

```bash
npm run preview
```

## 目录结构（精简）

```
src/
  data/          posts.js · series.js · projects.js · changelog.js · profile.js
  views/         页面
  components/    可复用组件
Content/         文章 HTML 正文
docs/            构建输出（勿手改）
scripts/         构建辅助脚本
```

## 环境变量

复制 `.env.example` 为 `.env`，按需配置 Twikoo、音乐 CDN 等（详见各部署笔记文章）。

## 技术栈

Vue 3 · Vite · Vue Router · Pinia · Prism.js · Twikoo

## 平台 v2（M1–M5.5 已完成 · M6 整站 ECS）

**方案 A 开发** + **M6 整站阿里云同域部署**（前端 + API 均在 ECS）。

- **后端 API**：[backend/README.md](backend/README.md)
- **M6 上线指南**：[deploy/README-m6-ecs.md](deploy/README-m6-ecs.md)
- **方案 A 本地开发**：[deploy/README-cloud-dev.md](deploy/README-cloud-dev.md)
- 工作流：[笔记/项目/CYINC动态主站工作流.md](笔记/项目/CYINC动态主站工作流.md)

## License

MIT（站点内容与图片除外，版权归作者所有）
