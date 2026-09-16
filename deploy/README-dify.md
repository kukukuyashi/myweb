# Dify 部署指南

> **本机无法装 Docker？** 请用 **方案 A**：[README-cloud-dev.md](./README-cloud-dev.md)（Dify Cloud + n8n Cloud）  
> 下文为 **ECS 自建**（M6 上线时使用）。

CYINC 平台通过 **Dify HTTP API** 调用一个 Workflow 应用：

| 应用 | 类型 | 环境变量 | 用途 |
|------|------|----------|------|
| 文章摘要 | Workflow | `DIFY_SUMMARY_API_KEY` | `POST /api/v1/posts/{id}/summary`、ACG 机器人文章润色 |

---

## 1. 安装 Docker Desktop

Windows 需先安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)，安装后重启。

验证：

```powershell
docker --version
docker compose version
```

---

## 2. 启动 Dify（官方 Compose）

```powershell
git clone https://github.com/langgenius/dify.git
cd dify/docker
copy .env.example .env
docker compose up -d
```

首次启动约 3～5 分钟。浏览器打开：

- 控制台：<http://localhost/install> 或 <http://localhost>（完成初始化）
- API 基址（默认）：`http://127.0.0.1/v1`（经 Nginx 80 端口）  
  若直连 API 容器：`http://127.0.0.1:5001/v1`

在 `backend/.env` 中设置：

```env
DIFY_API_URL=http://127.0.0.1/v1
DIFY_TIMEOUT_SEC=60
```

---

## 3. 配置 LLM 提供商

Dify 控制台 → **设置** → **模型供应商** → 添加 **通义千问 / DeepSeek / OpenAI** 等，填入 API Key。

> LLM Key 只存在 Dify 内，**不要**写入 CYINC 的 Git 仓库。

---

## 4. 创建「文章摘要」Workflow

1. **工作室** → **创建应用** → **工作流**
2. 开始节点添加输入变量：
   - `title`（文本）
   - `content`（段落）
3. 添加 **LLM** 节点，Prompt 示例：

```
请为以下博客生成：
1. 100字以内中文摘要（输出到 summary）
2. 3个标签建议（JSON 数组，输出到 suggested_tags）

标题：{{#title#}}
正文：{{#content#}}
```

4. 结束节点输出变量：`summary`、`suggested_tags`
5. **发布** → **API 访问** → 复制 **API Key** → 写入 `backend/.env`：

```env
DIFY_SUMMARY_API_KEY=app-xxxxxxxx
```

---

## 5. 验证

```powershell
# Swagger 登录后测试摘要接口
# http://127.0.0.1:8000/api/docs → POST /api/v1/posts/{id}/summary
```

返回摘要即配置成功；未配置时接口返回 503。

---

## 7. 生产环境建议

- Dify 与 FastAPI **同 ECS 内网**通信，不暴露 Dify 公网
- Nginx 只反代 CYINC 前端 + `/api`

---

## 故障排查

| 现象 | 处理 |
|------|------|
| `503 Dify 未配置` | 检查 `.env` 的 `DIFY_API_URL` / `DIFY_SUMMARY_API_KEY`，重启 uvicorn |
| Workflow 无 outputs | 确认 Dify 结束节点输出变量名为 `summary` |
| Docker 拉取失败 | 配置镜像加速或使用 VPN |
