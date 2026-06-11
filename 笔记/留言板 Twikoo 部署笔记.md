# 留言板 Twikoo 部署笔记

> 日期：2026-06-11  
> 博客：https://kukukuyashi.github.io/myweb/  
> 留言板页：https://kukukuyashi.github.io/myweb/guestbook

---

## 介绍

### Twikoo 是什么？

**Twikoo** 是一款**开源、轻量、可自建**的评论 / 留言系统，由国内开发者维护（[官方文档](https://twikoo.js.org/)）。名字来自「Twitter + 微博（weibo）+ 评论（comment）」的缩写组合。

它不是一个完整的论坛，而是一套可以**嵌入任意网页**的评论组件：你在页面里放一块区域，Twikoo 会自动渲染「输入框 + 留言列表 + 回复、点赞等交互」。

### 用来干什么？

常见用途：

| 场景 | 说明 |
|------|------|
| **博客留言板** | 单独一页，访客随便聊、打招呼、提建议（本博客 `/guestbook` 就是这样） |
| **文章评论** | 挂在每篇文章下面，针对正文讨论 |
| **静态站互动** | GitHub Pages、Vite、Hexo、Hugo 等没有后端的站点，也能有评论功能 |

本博客是 **Vue 静态站 + GitHub Pages**，本身不能存留言，所以需要 Twikoo 提供「后端 API + 数据库」。

### 和别的评论方案比

| 方案 | 特点 |
|------|------|
| **Disqus** | 省事，但数据在第三方、广告多、国内慢 |
| **Gitalk / Giscus** | 评论存在 GitHub Issues，适合技术博客，非 GitHub 用户难用 |
| **Twikoo** | 数据在自己 MongoDB 里，界面简洁，国内博主用得较多，免费云函数能跑 |

选 Twikoo 的原因：**留言数据自己掌控**，不依赖 GitHub 账号，免费额度对个人博客够用。

### Netlify 云函数是什么？

**Netlify** 是一个网站托管平台（类似「帮你把代码跑在服务器上」的服务）。**Netlify Functions（云函数）** 是它提供的一种 **Serverless 后端**：你不用自己买 VPS、装 Node.js，只要把 Twikoo 的后端代码部署上去，Netlify 会在有人访问时**临时启动一段程序**来处理请求。

可以把它理解成：

| 概念 | 通俗理解 |
|------|----------|
| **云函数** | 按需运行的一小段后端代码，像「按一下才工作的服务员」 |
| **Netlify** | 提供运行环境的平台，本笔记里负责跑 Twikoo 后端 |
| **envId** | 云函数的网址，前端 Twikoo JS 往这个地址发请求 |

**用来干什么？**

- 接收留言板发来的「发评论、拉评论列表」等请求  
- 校验内容、写入数据库、返回结果给浏览器  
- 本项目的 envId：`https://cyinc-twikoo.netlify.app/.netlify/functions/twikoo`

**为什么用 Netlify 而不是 Hugging Face？**

本次部署中 Hugging Face 免费 Docker Space 经常 **Paused / Preparing / 503**；Netlify 免费额度对个人博客留言够用，部署 twikoo-netlify 仓库即可，**相对稳定**。

### MongoDB Atlas 是什么？

**MongoDB** 是一种 **NoSQL 数据库**，数据以「文档」（类似 JSON）形式存储，适合存评论这种结构不固定的内容。**MongoDB Atlas** 是 MongoDB 官方提供的 **云端托管服务**，有免费套餐（M0），不用在自己电脑上装数据库。

可以把它理解成：

| 概念 | 通俗理解 |
|------|----------|
| **MongoDB** | 专门存数据的「仓库」，留言文字、昵称、时间都放这里 |
| **Atlas** |  MongoDB 的云版本，注册账号就能用，不用自己维护服务器 |
| **MONGODB_URI** | 连接串，告诉 Twikoo 后端「数据库在哪、用户名密码是什么」 |

**用来干什么？**

- **持久化保存**所有留言——关掉网页、重启云函数，数据仍在  
- Twikoo 后端通过 `MONGODB_URI` 连接 Atlas，读写 `comment` 等集合（表）  
- 本博客不直接连 MongoDB，只有 Netlify 上的 Twikoo 云函数会连

**免费够用吗？**

个人博客留言量很小，**M0 免费集群**足够；注意在 Atlas 里配置 **IP 白名单 `0.0.0.0/0`**，否则云函数连不上库。

### 三者在本项目里怎么配合？

一句话：**网页只负责显示；Netlify 负责处理请求；MongoDB 负责存数据。**

| 角色 | 技术 | 在本项目中的地址 / 配置 |
|------|------|-------------------------|
| 前端展示 | Twikoo JS + `Guestbook.vue` | 博客 `/guestbook` 页 |
| 后端逻辑 | Netlify Functions | envId → `…netlify.app/.netlify/functions/twikoo` |
| 数据存储 | MongoDB Atlas | Netlify 环境变量 `MONGODB_URI` |

```
访客在留言板输入内容
    → 浏览器里的 Twikoo 前端 JS 发送请求
    → Netlify 上的 Twikoo 云函数处理
    → MongoDB Atlas 保存 / 读取留言
    → 页面展示评论列表
```

博客代码里只需要：

1. 一个 `<div id="tcomment">` 容器（在 `Guestbook.vue`）
2. 加载 Twikoo 的 JS，并填入 **envId**（后端地址）

后面章节记录的是：**MongoDB、Netlify、博客构建** 怎么一步步配通。

---

## 一、今天做了什么（总览）

给个人博客接入了 **Twikoo 评论/留言系统**，访客可以在留言板页发表评论，数据存在 **MongoDB Atlas** 云数据库里。

整体分三层：

```
访客浏览器
    ↓ 加载 Twikoo 前端 JS
博客 Guestbook.vue（GitHub Pages 静态站）
    ↓ 请求云函数 API
Twikoo 后端（Netlify Functions）
    ↓ 读写数据
MongoDB Atlas（存留言内容）
```

**最终方案：Netlify + MongoDB Atlas + 博客 `.env.local`**

中间尝试过 Hugging Face Docker Space，因免费实例不稳定（Paused / Preparing / 503）放弃。

**Git 已 push**，相关 commit：

| Commit | 说明 |
|--------|------|
| `217d348` | 首次把 Twikoo envId 打进 GitHub Pages 构建 |
| `42e5b02` | 留言板加载状态、去掉「还没做好」占位文案 |
| `0b90c0b` | 从 Hugging Face 切换到 Netlify 后端 |

---

## 二、Twikoo 的三部分（技术组成）

上面「介绍」说了整体用途，这里补充三个具体模块：

| 模块 | 是什么 | 在本项目里 |
|------|--------|------------|
| **前端** | `twikoo.all.min.js`，从 CDN 加载 | `Guestbook.vue` 里动态引入 |
| **后端（云函数）** | 处理发评论、拉列表、管理员操作 | Netlify Functions |
| **数据库** | 存留言正文、昵称、时间等 | MongoDB Atlas 免费集群 |

三者通过 **envId**（后端 URL）串联；数据库通过 **MONGODB_URI**（连接串）与后端相连。

官方文档：https://twikoo.js.org/

---

## 三、MongoDB Atlas 配置（数据库）

### 3.1 注册与建集群

1. 打开 https://cloud.mongodb.com/ 注册
2. **Build a Database** → 选 **M0 FREE**（免费）
3. 区域选离国内近的（如 Singapore）
4. 集群名默认 `Cluster0` 即可

> 若已有 Cluster0，不用重复建，直接在 Connect 里拿连接信息。

### 3.2 创建数据库用户

**Security → Database Access → Add New Database User**

| 项 | 建议 |
|----|------|
| Authentication | Password |
| Username | `twikoo2`（任意英文名） |
| Password | **手动设纯字母数字**，如 `TwikooPass2026`（避免特殊字符要 URL 编码） |
| 权限 | **Built-in Role** → **Read and write to any database** 或 **Atlas admin** |

### 3.3 IP 白名单

**Security → Network Access → Add IP Address**

- 选 **Allow Access from Anywhere** → `0.0.0.0/0`
- Twikoo 云函数 IP 不固定，必须放行所有 IP（仍需要用户名+密码才能连库）

### 3.4 连接字符串（MONGODB_URI）

**Database → Clusters → Cluster0 → Connect → Drivers → Node.js**

Atlas 会给类似：

```
mongodb+srv://twikoo2:<db_password>@cluster0.atlgggo.mongodb.net/?appName=Cluster0
```

**重要：**

- `<db_password>` 是占位符，要换成真实密码
- **不要保留尖括号** `<` `>`
- 正确示例：

```
mongodb+srv://twikoo2:TwikooPass2026@cluster0.atlgggo.mongodb.net/?retryWrites=true&w=majority
```

### 3.5 常见错误

| 报错 | 原因 |
|------|------|
| `bad auth : authentication failed` | 密码错、用户名错、或连接串里还留着 `<db_password>` |
| 连不上 | 没加 `0.0.0.0/0` |

---

## 四、Hugging Face 尝试（已放弃，作踩坑记录）

### 4.1 做法

1. **New Space** → SDK 选 **Docker** + **Blank** + CPU Free
2. **Settings → Secret**：`MONGODB_URI` = 上面连接串
3. **Files → Dockerfile**：

```dockerfile
FROM imaegoo/twikoo
ENV TWIKOO_PORT 7860
EXPOSE 7860
```

4. envId 填 Direct URL：`https://用户名-space名.hf.space`

### 4.2 遇到的问题

| 现象 | 说明 |
|------|------|
| 选成 Gradio SDK | 会要求 `app.py`，Twikoo 跑不起来 |
| `bad auth` | 密码/尖括号问题（后来 v3 曾成功 `Connected to database`） |
| **Preparing Space 一直转** | 免费 Docker Space 冷启动极慢或失败 |
| **Paused** | 不用就自动休眠 |
| Restart / Factory reboot → **503** | 容器未就绪或反复重启 |

**结论：HF 免费 Docker 不适合当 Twikoo 长期在线后端。**

---

## 五、Netlify 部署（最终方案 ✅）

文档：https://twikoo.js.org/backend.html#netlify-部署

### 5.1 Fork 仓库

https://github.com/twikoojs/twikoo-netlify → **Fork** 到自己 GitHub（如 `kukukuyashi/twikoo-netlify`）

### 5.2 Netlify 导入

1. https://app.netlify.com/ → **Add new project → Import from Git → GitHub**
2. 授权时 **仅选择存储库** → 勾选 `twikoo-netlify`
3. **Deploy site**（先部署建站点）

### 5.3 环境变量（在 Netlify，不在 GitHub）

**Project configuration → Environment variables → Add a variable**

| Key | Value |
|-----|--------|
| `MONGODB_URI` | MongoDB 完整连接串（无尖括号） |

保存后：**Deploys → Trigger deploy → Deploy site**（必须 Redeploy 变量才生效）

### 5.4 站点名

**Domain management → Edit site name** → 设为 `cyinc-twikoo`

站点首页：https://cyinc-twikoo.netlify.app  
应显示：**Twikoo 云函数运行正常**

### 5.5 envId（给博客用）

Netlify 的 envId **不是**站点首页，要带函数路径：

```
https://cyinc-twikoo.netlify.app/.netlify/functions/twikoo
```

---

## 六、博客端接入

### 6.1 相关文件

| 文件 | 作用 |
|------|------|
| `src/views/Guestbook.vue` | 留言板页面，加载 Twikoo JS 并 `init` |
| `src/router/index.js` | 路由 `/guestbook` |
| `.env.local` | 本地环境变量（**不提交 Git**） |
| `.env.example` | 模板，可提交 |
| `docs/` | `npm run build` 产物，GitHub Pages 用 |

### 6.2 环境变量

项目根目录 `.env.local`：

```env
VITE_TWIKOO_ENV_ID=https://cyinc-twikoo.netlify.app/.netlify/functions/twikoo
```

Vite 会把 `VITE_` 前缀的变量打进构建产物，所以 **build 前必须有 `.env.local`**。

### 6.3 Guestbook.vue 逻辑简述

1. 页面挂载时动态加载 `https://cdn.jsdelivr.net/npm/twikoo@1.6.32/dist/twikoo.all.min.js`
2. 读取 `import.meta.env.VITE_TWIKOO_ENV_ID`
3. 调用 `window.twikoo.init({ envId, el: '#tcomment', lang: 'zh-CN' })`
4. `#tcomment` 容器内渲染评论框
5. 有 loading / error 提示（15 秒内未渲染出子元素则报 error）

### 6.4 构建与发布

```bash
npm run build          # 输出到 docs/，base 为 /myweb/
git add docs/
git commit -m "Enable Twikoo guestbook"
git push origin main
```

GitHub Pages 从 `main` 分支的 `docs/` 目录发布。

### 6.5 本地开发

```bash
npm run dev
# http://localhost:5173/myweb/guestbook
```

---

## 七、管理员设置

1. 打开留言板，等评论框出现
2. 点击评论框右下角 **齿轮图标**
3. 首次会要求设置 **管理员密码** 和 **暗号**
4. 之后可审核、回复、删除留言

Netlify 版支持管理面板；HF 版邮件功能受限。

---

## 八、安全相关（同一天其它事项）

### 8.1 GitHub Token

- 曾把 `ghp_` Token 写在 `git remote` URL 里 → **已在 GitHub 撤销**
- remote 已改为：`https://github.com/kukukuyashi/myweb.git`
- **以后**：HTTPS + 凭据管理器，或 SSH，不要把 Token 写进 URL

### 8.2 密钥不要进 Git

- `.env.local` 已在 `.gitignore`
- `MONGODB_URI` 只放在 Netlify Environment variables，不要写进仓库

---

## 九、故障排查速查

| 现象 | 检查 |
|------|------|
| 留言板空白 | `.env.local` 有无 envId；是否 `npm run build` 后 push |
| 「评论服务暂不可用」 | Netlify 是否 Published；打开 envId URL 是否「运行正常」 |
| 发评论失败 | F12 Console / Network；MongoDB IP、MONGODB_URI |
| 线上还是旧版 | Ctrl+Shift+R；等 GitHub Pages 1～2 分钟 |
| HF Preparing / 503 | 换 Netlify，别死磕 HF |

---

## 十、架构图（最终）

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Pages (静态)                                     │
│  kukukuyashi.github.io/myweb/guestbook                  │
│  Guestbook.vue + twikoo.js (CDN)                        │
└───────────────────────────┬─────────────────────────────┘
                            │ envId
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Netlify Functions                                       │
│  cyinc-twikoo.netlify.app/.netlify/functions/twikoo     │
│  (fork: twikoo-netlify)                                  │
└───────────────────────────┬─────────────────────────────┘
                            │ MONGODB_URI
                            ▼
┌─────────────────────────────────────────────────────────┐
│  MongoDB Atlas (M0 Free)                                 │
│  Cluster0 + 用户 twikoo2                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 十一、以后维护

### 换 Twikoo 后端地址

1. 改 `.env.local` 里的 `VITE_TWIKOO_ENV_ID`
2. `npm run build` → push `docs/`

### 换 MongoDB 密码

1. Atlas 改 Database User 密码
2. Netlify 更新 `MONGODB_URI`
3. Trigger redeploy

### 备份留言

数据在 MongoDB Atlas → **Database → Browse Collections**

---

## 十二、参考链接

- Twikoo 文档：https://twikoo.js.org/
- Twikoo Netlify 部署：https://twikoo.js.org/backend.html#netlify-部署
- twikoo-netlify 仓库：https://github.com/twikoojs/twikoo-netlify
- MongoDB Atlas：https://cloud.mongodb.com/
- 博客仓库：https://github.com/kukukuyashi/myweb

---

## 十三、一句话总结

> 留言板 = 博客里的 Twikoo 前端 + Netlify 云函数 + MongoDB 存数据。  
> 今天踩坑主要在 HF 不稳定和 MongoDB 连接串密码格式（**尖括号不能留**）。  
> 最终 Netlify 一次部署成功，博客 build 后 push 即可上线。
