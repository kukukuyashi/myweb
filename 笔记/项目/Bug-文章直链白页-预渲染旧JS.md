---
title: "Bug：文章直链白页 vs 站内正常（预渲染引用已删 JS）"
date: "2026-07-17"
category: "部署"
tags: ["Bug", "部署", "Vue", "预渲染", "SEO", "ECS", "缓存"]
excerpt: "朋友直接打开 /myweb/content/29 看到白底静态文，自己从站内点进去却是完整深色站：根因是预渲染 HTML 仍引用旧 hashed JS，热更 assets 后旧文件已删、Vue 无法挂载。"
cover: "img/bgm/2.jfif"
---

# Bug：文章直链白页 vs 站内正常（预渲染引用已删 JS）

> 写于 2026-07-17 · CYINC 博客上线 ECS 后的一次「同 URL、不同人看到不一样」复盘  
> 现象入口：`https://cyinc.ink/myweb/content/29`

---

## 一、现象（大白话）

| 谁 | 怎么进 | 看到什么 |
|----|--------|----------|
| 你 | 从首页 / 归档 **站内点进** 文章 | 完整站：顶栏 CYINC.LOG、侧栏目录、深色主题（Vue SPA） |
| 朋友 | **浏览器地址栏直接打开** `/myweb/content/29` | 白底、无导航、只有正文 —— 像「简陋 HTML」 |

同一路径，不是两套设计，而是 **两层页面**：

1. **预渲染兜底页**（给搜索引擎 / JS 未跑通时看）  
2. **Vue 交互站**（JS 加载成功后替换 `#app`）

朋友卡在了第 1 层；你走的是第 2 层。

预渲染页底部原本就有说明（大意）：

> 静态预览供搜索引擎阅读；交互版由 Vue 加载后替换本区域。

---

## 二、请求链路（为什么「直链」和「站内」不一样）

```text
A. 站内跳转（你）
   已加载过 /myweb/index.html
   → 当前入口 JS（例如 index-DHmYUF43.js）已在内存
   → router 切到 /content/29
   → 直接渲染完整 Content.vue ✅

B. 直链打开（朋友）
   Nginx 命中预渲染文件：
   /var/www/cyinc/myweb/content/29/index.html
   → 该 HTML <head> 里写死了构建时的：
        /myweb/assets/index-8E644akY.js
        /myweb/assets/index-CLHQzojC.css
   → 若这两份文件已被新部署删掉 → 404
   → Vue 起不来 → 永远停在白底 prerender-fallback ❌
```

**关键词：**

| 词 | 含义 |
|----|------|
| **预渲染（Prerender）** | 构建时把文章正文塞进静态 HTML，方便 SEO / 无 JS 也能读到字 |
| **hashed 资源名** | Vite 打包后 `index-xxxxx.js`，文件名带内容哈希；一改代码哈希就变 |
| **SPA** | 单页应用：多数路由靠前端 JS 切换，不只靠服务器上每个路径一份「完整站」 |

---

## 三、根因（这次是怎么踩的）

线上曾用「只换前端壳」的方式热更：

```bash
# 大致做法（问题出在这里）
rm -rf /var/www/cyinc/myweb/assets
# 解压新的 assets/ + 根目录 index.html
# ❌ 没有同步更新 content/*/index.html、tags/*/index.html 等预渲染页
```

结果：

| 文件 | 状态 |
|------|------|
| `/myweb/index.html` | 已指向 **新** `index-DHmYUF43.js` |
| `/myweb/assets/` | 只剩 **新** hashed 文件 |
| `/myweb/content/29/index.html` | 仍指向 **旧** `index-8E644akY.js`（文件已不存在） |

所以：

- 从首页进 = 用新入口 → 正常  
- 分享链接 / 收藏夹 / 朋友直开文章 = 旧预渲染 → JS 404 → 白页  

用浏览器开发者工具 Network 一看：直链页面的 `index-8E644akY.js` 会是 **404**，即可一锤定音。

---

## 四、修复（当时怎么处理的）

1. 本机完整构建（至少保证 `docs/index.html` 与 `docs/assets` 一致）  
2. 跑预渲染脚本，按**当前** `index.html` 里的资源名重写所有路由 HTML：

```bash
npx vite build --base /myweb/
node scripts/generate-prerender.mjs docs
```

3. 把 `docs/` 里带哈希引用的预渲染树同步到 ECS（至少）：

- `index.html`
- `content/**`
- `tags/**`
- 以及 `about` / `archive` / `projects` / `changelog` / `guestbook` / `music` 等 prerender 目录（若有）

4. 验收：

```bash
# 预渲染页引用的 JS，必须在 assets 里真实存在
grep -oE 'assets/index-[^"]+\.js' /var/www/cyinc/myweb/content/29/index.html
ls /var/www/cyinc/myweb/assets/index-*.js

# 无痕/强制刷新直开
# https://cyinc.ink/myweb/content/29
```

朋友侧若仍白页：让对方 **强制刷新 / 清缓存**（旧 HTML 可能被浏览器或中间缓存住）。

---

## 五、以后怎么避免（部署清单）

### 5.1 前端部署「整包一致」

每次上线前端，下列必须 **同一轮构建产物**：

| 必更 | 说明 |
|------|------|
| `assets/` | 新 hashed JS/CSS |
| `index.html` | 入口引用 |
| `content/**` 等预渲染 HTML | 同样引用那一套 hashed 文件 |

只换 `assets/` + 根 `index.html`、留下旧 `content/*/index.html` = **必现本 Bug**。

推荐流程：

```bash
npm run build          # 内含 vite + generate-prerender 等
# 再 rsync/解压整个 docs/ → /var/www/cyinc/myweb/
# 或至少：assets + index.html + content + tags + …
```

### 5.2 快速自检（上线后 30 秒）

```bash
ROOT=/var/www/cyinc/myweb
NEW=$(grep -oE 'index-[^"]+\.js' "$ROOT/index.html" | head -1)
OLD=$(grep -oE 'index-[^"]+\.js' "$ROOT/content/29/index.html" | head -1)
echo "root=$NEW article=$OLD"
test "$NEW" = "$OLD" && echo OK || echo BROKEN_PRERENDER_HASH_MISMATCH
test -f "$ROOT/assets/$NEW" && echo ASSET_OK || echo ASSET_MISSING
```

根入口与任意一篇 `content/*/index.html` 的 `index-*.js` **必须相同**，且文件存在。

### 5.3 和「主题 / 评论」无关

| 易混淆 | 实际 |
|--------|------|
| 「朋友主题是浅色」 | 那是兜底 CSS，不是主题系统 |
| 「评论删了所以变白」 | 无关；白页是 SPA 没挂上 |
| 「只有朋友电脑有问题」 | 直链 + 过期预渲染时，任何人都会中招 |

---

## 六、相关代码 / 脚本

| 路径 | 作用 |
|------|------|
| `scripts/generate-prerender.mjs` | 按 `docs/index.html` 模板生成各路由静态 HTML |
| `src/views/Content.vue` | 交互版文章页（导航、侧栏、阅读进度等） |
| 预渲染 HTML 中的 `.prerender-fallback` | JS 未替换前的白底正文 |

相关笔记：

- [ECS 生产排障：论坛 Token 无效与登录 502](./ECS生产排障-论坛Token无效与登录502.md)  
- [线上笔记管理台：/myweb/admin](./线上笔记管理台-myweb-admin.md)  
- `deploy/README-m6-ecs.md`（前端同步说明）

---

## 七、一句话结论

**热更前端时若只换 `assets/` 而不重生/不同步预渲染 HTML，直链文章会引用已删除的 hashed JS，Vue 挂不上，访客只能看到 SEO 白底页；站内跳转因已持有新入口 JS 而看起来「一切正常」。**
