# Dify 部署指南

> **本机无法装 Docker？** 请用 **方案 A**：[README-cloud-dev.md](./README-cloud-dev.md)（Dify Cloud + n8n Cloud）  
> 下文为 **ECS 自建**（M6 上线时使用）。

CYINC 平台通过 **Dify HTTP API** 调用两个应用：

| 应用 | 类型 | 环境变量 | FastAPI 路径 |
|------|------|----------|--------------|
| 文章摘要 | Workflow | `DIFY_SUMMARY_API_KEY` | `POST /api/v1/ai/summary`、`POST /api/v1/posts/{id}/summary` |
| 站内助手 | Chatflow + 知识库 | `DIFY_CHAT_API_KEY` | `POST /api/v1/ai/chat` |

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

## 5. 创建「站内 AI 助手」Chatflow

1. **创建应用** → **聊天助手**（或 Chatflow）
2. **知识库** → 新建 → 上传博客 Markdown/HTML 转文本
3. 在应用中关联知识库，开启 RAG
4. 发布 → 复制 API Key：

```env
DIFY_CHAT_API_KEY=app-yyyyyyyy
```

5. 前端访问：<http://localhost:5173/myweb/ai>（需先登录平台账号）

---

## 6. 验证

```powershell
# 后端健康 + Dify 配置状态
curl http://127.0.0.1:8000/api/v1/ai/status

# Swagger 登录后测试
# http://127.0.0.1:8000/api/docs
```

`ai/status` 返回 `"chat_ready": true` / `"summary_ready": true` 即配置成功。

---

## 7. 生产环境建议

- Dify 与 FastAPI **同 ECS 内网**通信，不暴露 Dify 公网
- Nginx 只反代 CYINC 前端 + `/api`
- 知识库定期用脚本同步新文章

---

## 故障排查

| 现象 | 处理 |
|------|------|
| `503 Dify 未配置` | 检查 `.env` 三个 DIFY_* 变量，重启 uvicorn |
| Workflow 无 outputs | 确认 Dify 结束节点输出变量名为 `summary` |
| Chat 无 answer | 确认 Chatflow 已发布且 API Key 正确 |
| Docker 拉取失败 | 配置镜像加速或使用 VPN |
