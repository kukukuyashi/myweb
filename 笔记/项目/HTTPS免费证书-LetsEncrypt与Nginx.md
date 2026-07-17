---
title: "HTTPS 免费证书：为什么要把 HTTP 改成 HTTPS"
date: "2026-07-15"
category: "部署"
tags: ["部署", "HTTPS", "SSL", "Let's Encrypt", "Nginx", "备案", "ECS"]
excerpt: "备案通过、域名 cyinc.ink 可访问后，用 Let's Encrypt + Certbot 给 Nginx 免费上 HTTPS。讲清 HTTP/HTTPS、证书、为什么要做、怎么做、容易踩的坑，并解释专有名词。"
cover: "img/bgm/2.jfif"
---

# HTTPS 免费证书：为什么要把 HTTP 改成 HTTPS

> 写于 2026-07-15 · CYINC（`cyinc.ink`）管局备案通过后的真实操作  
> 结果：证书签发成功，Nginx 已启用 `https://cyinc.ink` 与 `https://www.cyinc.ink`，到期约 2026-10-13，后台可自动续期。

---

## 一、用大白话先说结论

| 问题 | 一句话答案 |
|------|------------|
| HTTP 和 HTTPS 差在哪？ | HTTP 像明信片，路上谁都能看；HTTPS 像封好的信封，别人偷看很难 |
| 证书是什么？ | 浏览器认的「营业执照」：证明这个 `cyinc.ink` 真的是你家服务器，并且通信会被加密 |
| 免费证书靠谱吗？ | 个人/博客站点常用 **Let’s Encrypt**，全球大量网站在用，三个月一换，工具可自动续 |
| 我这次做了什么？ | 在阿里云 ECS 上，用 **Certbot** 让 Nginx 自动装上 HTTPS，并建议把站点配置里的 `http://` 改成 `https://` |

---

## 二、为什么要把 HTTP 改成 HTTPS（做这事的意义）

### 2.1 安全：防窃听、防篡改

用户登录、发帖、Cookie、Token 都会在浏览器和服务器之间来回传。

- **只用 HTTP**：数据基本是明文。在不可信 Wi‑Fi、中间环节上，有人理论上能偷看或改一点内容。  
- **上了 HTTPS**：内容被加密。第三方即使截到数据包，也很难读懂「密码是什么」「token 是什么」。

可以把它想成：

> HTTP = 大喊着报密码；HTTPS = 用只有你和柜台听得懂的暗号说话。

### 2.2 身份：证明「这个域名就是这台站」

HTTPS 依赖 **证书（Certificate）**。浏览器会检查：

1. 证书是不是受信任的机构签发（如 Let’s Encrypt）  
2. 证书上的域名是否跟地址栏一致（是不是真的 `cyinc.ink`）  
3. 证书有没有过期、有没有被吊销  

这样可降低「假冒你域名的钓鱼站」成功概率（再配合正确的 DNS、不要泄露私钥）。

### 2.3 产品与信任：小锁、现代浏览器习惯

- 浏览器对纯 HTTP 会标「不安全」  
- 不少新 API、PWA、部分 Cookie 策略更偏向 HTTPS  
- 简历 / 作品集站点用 `https://cyinc.ink` 更正规  

备案解决的是「域名能不能在国内访问」；**HTTPS 解决的是「访问时通不通、安不安全」。两件事先先后，都要。**

### 2.4 和「整站同域」的关系（结合本项目）

CYINC 生产形态大致是：

```text
用户浏览器
    ↓  https://cyinc.ink/...
Nginx（80/443）
    ├─ /myweb/     → 静态前端
    ├─ /api        → FastAPI
    └─ /admin      → SQLAdmin
```

上 HTTPS 之后：

- 前端、接口、后台管理都走同一套安全连接  
- 登录后的 Token / Cookie 不再裸奔在明文 HTTP 上  
- 后端 `.env` 里的 `CORS_ORIGINS`、`PUBLIC_SITE_URL` 也应写成 `https://...`，避免前端以为在安全页、后端却按 HTTP 源放行导致各种诡异跨域或跳转问题  

---

## 三、专有名词小词典（尽量白话）

| 名词 | 是什么 | 可以怎么理解 |
|------|--------|--------------|
| **HTTP** | 网页传输的老协议，默认端口 **80** | 寄明信片 |
| **HTTPS** | HTTP + 加密与身份校验，默认端口 **443** | 寄密封挂号信 |
| **SSL / TLS** | 底下真正负责加密的协议族；日常口语里常被笼统叫「SSL」 | 「信封装技术」；现在实际用的多是 **TLS** |
| **证书（Certificate）** | 一串文件，证明「我控制这个域名」并配合加密 | 门店的营业执照 |
| **公钥 / 私钥** | 证书体系里一对钥匙。公钥可以公开，私钥必须锁在服务器上 | 公钥 = 锁；私钥 = 唯一的钥匙。私钥泄露 = 别人能冒充你 |
| **证书颁发机构（CA）** | 签发证书的受信任机构 | 公证处 / 发证机关 |
| **Let’s Encrypt** | 一家免费、自动化的 CA | 「免费自动盖章的公证处」 |
| **Certbot** | 帮你向 Let’s Encrypt 申请证书、并改 Nginx 配置的工具 | 「一键办证 + 装进网站」的助手 |
| **ACME** | 申请证书时的自动协议 | Certbot 跟 Let’s Encrypt「对暗号」的流程名 |
| **完整证书链（fullchain）** | 你的证书 + 中间证书，浏览器用来一路验证到根信任 | 营业执照 + 上级批文复印件 |
| **私钥（privkey）** | 绝不能公开的那把钥匙 | 仓库钥匙；不要贴进 Git、不要发聊天 |
| **Nginx** | 本站前面的「门面服务」：静态文件 + 反向代理到 API | 大楼前台，再决定去哪个房间 |
| **反向代理** | 对外一个域名端口，对内转发到 `127.0.0.1:8000` 等 | 前台代你对接后台柜员 |
| **DNS / A 记录** | 把域名翻译成 IP | 通讯录里的姓名 → 电话号码 |
| **安全组** | 云服务器防火规则 | 小区门禁：只允许哪些端口从外网进来 |
| **强制跳转（Redirect）** | 访问 `http://` 自动变成 `https://` | 大门只留加密通道 |
| **续期（Renew）** | Let’s Encrypt 证书大约 **90 天** 有效，到期前自动换新 | 每季度换一次临时通行证；Certbot 可自动办 |

---

## 四、什么时候适合做（以及你做的时机）

本项目真实顺序是：

1. 域名买好、解析到 ECS  
2. **ICP 备案**通过（管局审核过，域名不再被「未备案拦截」）  
3. `http://cyinc.ink` 已能打开站点  
4. Nginx 的 `server_name` 已是 `cyinc.ink www.cyinc.ink`  
5. 再用 Certbot 上 HTTPS  

**注意：** 备案没过时，域名可能被运营商/云厂商拦。那种情况下你先折腾证书，往往验证域名时就会卡死。所以经验是：

> **先让 HTTP 域名稳定能打开，再申请 HTTPS。**

---

## 五、怎么做（按 CYINC 实操精简版）

### 5.1 预先条件 Checklist

- [ ] DNS：`cyinc.ink`（及如需要的 `www`）A 记录指向 ECS IP  
- [ ] 安全组放行 **80、443**（申请时常用 80 做验证）  
- [ ] Nginx 已启用站点，且 `server_name cyinc.ink www.cyinc.ink;`  
- [ ] 浏览器能打开 `http://cyinc.ink/myweb/`  

### 5.2 测配置并重载 Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

应看到 `syntax is ok` / `test is successful`。

### 5.3 安装 Certbot

```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
```

### 5.4 申请并部署证书

主域名 + www：

```bash
sudo certbot --nginx -d cyinc.ink -d www.cyinc.ink
```

交互时：

| 提示 | 怎么选 |
|------|--------|
| 邮箱 | 填能收到邮件的地址（续期告警用） |
| 同意服务条款 | **`Y`** |
| 是否把邮箱分享给 EFF | 可选，一般 **`N`** |
| 是否把 HTTP 跳到 HTTPS | 选 **`2`（Redirect）** 更省心 |

成功时你会看到类似：

```text
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/cyinc.ink/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/cyinc.ink/privkey.pem
Successfully deployed certificate for cyinc.ink ...
Congratulations! You have successfully enabled HTTPS ...
```

本站实际签发结果（备忘）：

- 证书目录：`/etc/letsencrypt/live/cyinc.ink/`  
- 到期日示例：约 **2026-10-13**（以 `sudo certbot certificates` 为准）  
- Certbot 已写入 `/etc/nginx/sites-enabled/cyinc`，并设置后台自动续期任务  

### 5.5 验证

浏览器：

- https://cyinc.ink/myweb/  
- https://cyinc.ink/api/health  
- https://cyinc.ink/admin  

服务器：

```bash
curl -I https://cyinc.ink/myweb/
curl -sf https://cyinc.ink/api/health
sudo certbot renew --dry-run
sudo certbot certificates
```

`--dry-run` 成功 ≈ 自动续期链路健康。

### 5.6 证书通过后建议改后端环境

`backend/.env`（路径以 ECS 上为准，常见 `/var/www/cyinc/backend/.env`）：

```env
CORS_ORIGINS=https://cyinc.ink
PUBLIC_SITE_URL=https://cyinc.ink/myweb
```

改完后需要 **重建/重启 API 容器**（只 `restart` 不一定重新读入 `env-file`，视你当初怎么起的容器而定）。  
目的：避免前端已是 HTTPS，后端仍按 HTTP / IP 配置 CORS、外链。

---

## 六、做的时候有什么要避免（坑位清单）

### 6.1 申请前

| 要避免 | 为什么 | 怎么办 |
|--------|--------|--------|
| 备案未过就强开 HTTPS | 域名可能被拦，ACME 验证失败 | 先 HTTP 通域名，再申请 |
| `server_name` 还是 IP 或写错域名 | Certbot 改的是对应站点；验证也对不上 | 先改成真实域名再 `nginx -t && reload` |
| 只申请了 `cyinc.ink`，却用 `www` 访问 | www 没有证书或未解析 | DNS 配好后一次加上 `-d www.cyinc.ink` |
| 安全组没开 **80** | Let’s Encrypt 常用 HTTP-01 验证，走 80 | 临时也必须保证验证时 80 可达 |
| 同一域名短时间狂点申请 | Let’s Encrypt **速率限制** | 失败先查日志，不要连续盲重试 |

### 6.2 申请中 / 成功后

| 要避免 | 为什么 | 怎么办 |
|--------|--------|--------|
| 把 `privkey.pem` 提交进 Git / 发群 | 私钥泄露 ≈ 别人可冒充你的站 | 私钥只留服务器；权限收紧 |
| 以为「证书装好 = 一切配置自动变 https」 | 前端构建变量、`.env`、外链可能还写死 `http://` | 查 `CORS_ORIGINS`、`PUBLIC_SITE_URL`、文档里的示例链接 |
| 用 **IP** 访问却期望绿锁 | 证书签的是域名，不是 IP | 用 `https://cyinc.ink` 访问 |
| 手动乱改 `/etc/letsencrypt` 里的文件 | 续期机制可能坏 | 证书交给 Certbot；站配置改 `sites-available` |
| 关掉 80 后不理续期 | 某些续期/验证方式仍可能依赖 80 | 保持 80 对公网开放，或改用 DNS 验证（更复杂） |
| 容器 / 多台机各装一份却 DNS 只指一台 | 验证落到错误机器 | 确认解析目标就是跑 Certbot 的那台 Nginx |

### 6.3 和本站特别相关的

- 生产是 **Nginx 反代 Docker 里的 API**：证书装在 **Nginx** 上即可，一般不用给容器再单独装一份网页证书。  
- 用户仍用旧书签打开 `http://IP/...`：那是另一条入口；长期应以域名为准，并尽量统一跳到 HTTPS 域名。  
- 页脚还要按备案要求挂 **ICP 号**（与 HTTPS 是两件独立合规事项）。

---

## 七、证书装在哪、自动续期是怎么回事

成功后，Certbot 会管两类东西：

1. **证书文件**（示意）  
   - `/etc/letsencrypt/live/cyinc.ink/fullchain.pem`  
   - `/etc/letsencrypt/live/cyinc.ink/privkey.pem`  
2. **Nginx 配置**里挂上 `ssl_certificate` / `ssl_certificate_key`，并（若选了）把 80 跳到 443  

续期：

- 证书大约 **90 天** 有效  
- 系统里一般有 **systemd timer** 或 **cron**，会定期跑 `certbot renew`  
- 临近到期会换新文件，并 reload Nginx  
- 你用 `sudo certbot renew --dry-run` 可以**演习**一遍（不真换证）

这就是「免费但不需要每三个月手工点一次」的关键。

---

## 八、和阿里云「免费 SSL 证书」怎么选

| 方式 | 优点 | 缺点 |
|------|------|------|
| **Certbot + Let’s Encrypt**（本次采用） | 免费、自动化、和 Nginx 集成好、续期省心 | 需 80/443 与域名解析正确；交互几步 |
| 阿里云控制台免费证书 | 控制台可视化 | 往往要下载、手动配 Nginx、续期也要自己盯 |

个人博客 / 作品集站：**Certbot 通常更省事**。

---

## 九、一句话回顾（面试也能说）

> 备案解决「域名能否在国内访问」；HTTPS 解决「访问是否加密、浏览器是否信任」。  
> 我在备案通过、HTTP 域名可访后，用 Let’s Encrypt 经 Certbot 为 Nginx 签发免费证书，开启 443，并将 HTTP 跳转到 HTTPS；私钥只存服务器，证书约 90 天由定时任务自动续期。同时把后端 CORS / 站点公网 URL 改成 `https://`，避免协议不一致。

---

## 十、本次操作速查（cyinc.ink）

```bash
# 已确认
# server_name cyinc.ink www.cyinc.ink;
sudo nginx -t && sudo systemctl reload nginx

sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d cyinc.ink -d www.cyinc.ink
# 邮箱 → Y → N → Redirect 选 2

curl -I https://cyinc.ink/myweb/
curl -sf https://cyinc.ink/api/health
sudo certbot renew --dry-run
```

相关：

- [deploy/README-m6-ecs.md](../../deploy/README-m6-ecs.md) · HTTPS 小节  
- [deploy/nginx.conf.example](../../deploy/nginx.conf.example)  
- [ECS生产排障-论坛Token无效与登录502.md](./ECS生产排障-论坛Token无效与登录502.md) · 同域 Nginx / API 链路  

---

*笔记结束。若后续把页脚 ICP、公安备案或 `.env` 切换到全站 HTTPS 也踩过坑，可在本文追加一节「上线后合规与配置对齐」。*
