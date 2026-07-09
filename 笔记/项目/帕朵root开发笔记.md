---
title: "帕朵root开发笔记"
date: "2026-06-14"
category: "项目"
tags: ["项目"]
excerpt: "帕朵root开发笔记 — 学习笔记。"
cover: "img/bgm/2.jfif"
---
## 开头

在这里写正文…
# 帕朵root 开发笔记

> 一个在 QQ 群里被 @ 会回复、偶尔冒泡说话、发表情包的 AI 机器人。
> 
> 本文档从开发者的角度，记录这个项目是怎么做的、怎么用的、每个模块是干什么的。

---

## 目录

- [项目概述](#项目概述)
- [技术栈总览](#技术栈总览)
- [整体架构](#整体架构)
- [环境搭建](#环境搭建)
- [NapCat 协议端配置](#napcat-协议端配置)
- [NoneBot2 框架详解](#nonebot2-框架详解)
- [核心插件模块详解](#核心插件模块详解)
  - [入口文件 \_\_init\_\_.py](#入口文件-__init__py)
  - [配置中心 config.py](#配置中心-configpy)
  - [AI 对话引擎 ai.py](#ai-对话引擎-aipy)
  - [人设定义 persona.py](#人设定义-personapy)
  - [回复润色 polish.py](#回复润色-polishpy)
  - [消息处理入口 at\_reply.py](#消息处理入口-at_replypy)
  - [随机冒泡 random\_chat.py](#随机冒泡-random_chatpy)
  - [复读机 repeat.py](#复读机-repeatpy)
  - [消息规则 rules.py](#消息规则-rulespy)
  - [消息解析 message\_context.py](#消息解析-message_contextpy)
  - [视觉识别 vision.py](#视觉识别-visionpy)
  - [RAG 知识库 knowledge.py](#rag-知识库-knowledgepy)
  - [长期记忆 memory.py](#长期记忆-memorypy)
  - [群号管理 group\_store.py](#群号管理-group_storepy)
  - [文案模板 replies.py](#文案模板-repliespy)
- [数据文件说明](#数据文件说明)
- [配置项详解](#配置项详解)
- [如何自定义](#如何自定义)
- [常见问题](#常见问题)

---

## 项目概述

这个项目是一个 **QQ 群聊 AI 机器人**，角色名叫「帕朵」。它不是那种一板一眼的客服机器人，而是一个模拟真实群友行为的话痨网友——会接梗、会吐槽、偶尔犯贱，但不会骂人。

### 它能干什么？

1. **被 @ 回复**：群里有人 @ 它，它会用 AI 生成回复（而不是固定话术）
2. **看图说话**：发图片或表情包给它，它能"看懂"图片内容并做出反应
3. **随机冒泡**：定时在群里随机发言或发表情包，制造"活人感"
4. **复读机**：群里连续两个人发了同样的内容，它会跟着复读（经典 QQ 群行为）
5. **长期记忆**：记住每个群友说过的话、喜好、梗，在后续对话中自然地用上
6. **知识库检索**：可以往 `data/knowledge/` 里放文件，机器人聊天时会自动检索相关内容

---

## 技术栈总览

先用大白话解释一下这些技术名词：

| 技术 | 大白话解释 |
|------|-----------|
| **Python** | 编程语言，这个项目的主要语言 |
| **NoneBot2** | 一个 Python 写的 QQ 机器人框架，帮你处理消息收发、插件管理等底层事情，你只需要写"收到消息后怎么回复" |
| **NapCat** | QQ 协议端，负责登录 QQ 小号、收发 QQ 消息。它把 QQ 的消息翻译成一种标准格式（OneBot11），让 NoneBot2 能读懂 |
| **OneBot11** | 一套消息格式标准，规定了"消息长什么样"。NapCat 按这个格式发消息，NoneBot2 按这个格式收消息 |
| **WebSocket** | 一种"长连接"通信方式。NapCat 和 NoneBot2 之间通过 WebSocket 实时传消息，就像打电话一样一直通着 |
| **FastAPI** | 一个 Python 的 Web 框架，NoneBot2 用它来提供 HTTP 和 WebSocket 服务 |
| **httpx** | 一个 Python 的 HTTP 客户端库，用来调用 AI API（发请求、收回复） |
| **APScheduler** | 定时任务调度器，用来实现"每隔 X 分钟检查一次要不要冒泡" |
| **Pydantic** | 数据验证库，用来定义配置项的类型和默认值 |
| **RAG** | Retrieval-Augmented Generation（检索增强生成），大白话就是"先从知识库里找相关内容，再喂给 AI 让它参考着回答" |
| **OpenAI 兼容 API** | 和 OpenAI 的接口格式一样的 API 服务。这个项目用的是小米 MiMo，但接口格式和 OpenAI 一样，所以代码不用改 |

---

## 整体架构

```
+-----------------+    WebSocket (反向WS)    +------------------+
|   NapCat 协议端  | <---------------------> |  NoneBot2 框架    |
|  (Nap_node/)     |   ws://127.0.0.1:8090   |  (bot.py)        |
|                  |   /onebot/v11/ws         |                  |
|  - 登录 QQ 小号   |                          |  - 消息路由       |
|  - 收发 QQ 消息   |                          |  - 插件管理       |
|  - OneBot11 协议  |                          |  - HTTP API 服务  |
+-----------------+                          +--------+---------+
                                                      |
                                              +-------+---------+
                                              |  kalulu 插件      |
                                              |  (src/plugins/)   |
                                              |                   |
                                              |  +-------------+ |
                                              |  | @回复 (入口)  | |
                                              |  | 随机冒泡      | |
                                              |  | 复读机        | |
                                              |  +------+------+ |
                                              |         |        |
                                              |  +------+------+ |
                                              |  | AI 对话引擎  | |
                                              |  |  - 会话历史  | |
                                              |  |  - 人设prompt| |
                                              |  |  - RAG知识   | |
                                              |  |  - 长期记忆  | |
                                              |  |  - 视觉识别  | |
                                              |  |  - 回复润色  | |
                                              |  +------+------+ |
                                              |         |        |
                                              +---------+--------+
                                                        |
                                               +--------+--------+
                                               |  OpenAI 兼容 API |
                                               |  (小米 MiMo)     |
                                               +-----------------+
```

**简单来说**：NapCat 登录 QQ 收消息 -> 通过 WebSocket 转发给 NoneBot2 -> NoneBot2 把消息交给 kalulu 插件处理 -> 插件调用 AI API 生成回复 -> 回复通过 NapCat 发回 QQ 群。

---

## 环境搭建

### 1. 安装 Python

需要 Python 3.9 或更高版本。从 python.org 下载安装。

### 2. 创建虚拟环境

虚拟环境就像一个"隔离间"，把项目的依赖和系统的 Python 隔开，避免互相干扰。

```powershell
cd d:\帕朵root
python -m venv .venv           # 创建虚拟环境
.\.venv\Scripts\Activate.ps1   # 激活虚拟环境（命令行前面会出现 (.venv) 标识）
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

`requirements.txt` 里列了 4 个依赖：
- `nonebot2[fastapi]` -- 机器人框架 + Web 服务器
- `nonebot-adapter-onebot` -- OneBot11 消息格式适配器
- `nonebot-plugin-apscheduler` -- 定时任务插件
- `httpx` -- HTTP 客户端，用来调 AI API

### 4. 配置文件

配置都在 `.env.prod` 里，后面会详细讲每个配置项。

---

## NapCat 协议端配置

### 什么是 NapCat？

QQ 官方没有提供公开的机器人接口（以前有，后来关了）。NapCat 是第三方开发的 QQ 协议端，它模拟 QQ 客户端的行为，登录一个 QQ 小号，然后把收到的消息转换成标准格式（OneBot11）发给你的机器人程序。

### 为什么需要"协议端"？

你可以把 NapCat 理解为一个"翻译官"：
- QQ 群里的消息是 QQ 自己的格式 -> NapCat 把它翻译成 OneBot11 格式
- 你的机器人想发消息到 QQ 群 -> NapCat 把 OneBot11 格式翻译回 QQ 格式

### 安装和配置

项目里已经包含了 NapCat（在 `Nap/` 和 `Nap_node/` 目录下）。

**启动顺序很重要**：先启动 NoneBot2，再启动 NapCat。

1. 启动 NoneBot2 后，它会在 `ws://127.0.0.1:8090` 监听连接
2. 打开 NapCat 的 WebUI（通常是 `http://127.0.0.1:6099`）
3. 在 WebUI 里配置"网络连接"：
   - 类型：**反向 WebSocket**（Reverse WS）
   - URL：`ws://127.0.0.1:8090/onebot/v11/ws`
   - Token：和 `.env.prod` 里的 `ONEBOT_ACCESS_TOKEN` 一致（如果没设就留空）
4. 保存后 NapCat 会自动连接 NoneBot2

### 反向 WebSocket 是什么意思？

普通的 WebSocket 是客户端主动连服务器。"反向"的意思是：NoneBot2 是服务器，NapCat 是客户端，由 NapCat 主动连过来。这样 NoneBot2 只需要等着就行，不用知道 NapCat 在哪里。

### 安全提醒

> **重要**：使用第三方协议端存在封号风险，一定要用小号，不要用主号！

---

## NoneBot2 框架详解

### bot.py -- 项目入口

```python
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

nonebot.init()                           # 初始化 NoneBot2
driver = nonebot.get_driver()            # 获取驱动（管理连接）
driver.register_adapter(ONEBOT_V11Adapter)  # 注册 OneBot V11 适配器
nonebot.load_from_toml("pyproject.toml")    # 从 pyproject.toml 加载插件配置

if __name__ == "__main__":
    nonebot.run()                        # 启动！
```

**大白话解释**：
- `nonebot.init()` -- 启动框架，读取 `.env.prod` 里的配置
- `register_adapter` -- 告诉 NoneBot2 "我会收到 OneBot11 格式的消息，你要会处理"
- `load_from_toml` -- 从 `pyproject.toml` 里读取要加载哪些插件
- `nonebot.run()` -- 开始运行，监听端口等待 NapCat 连接

### pyproject.toml -- 插件声明

```toml
[tool.nonebot]
adapters = [
    { name = "OneBot V11", module_name = "nonebot.adapters.onebot.v11" }
]
plugins = ["nonebot_plugin_apscheduler"]   # 第三方插件（定时任务）
plugin_dirs = ["src/plugins"]              # 自定义插件目录
```

NoneBot2 会自动扫描 `src/plugins/` 目录下的所有 Python 包，把它们当作插件加载。所以 `src/plugins/kalulu/` 会被自动发现和加载。

### NoneBot2 的核心概念

- **事件（Event）**：收到一条消息就是一个"事件"
- **处理器（Handler）**：收到事件后执行的函数
- **规则（Rule）**：决定是否要处理这个事件的条件
- **适配器（Adapter）**：把不同格式的消息翻译成统一格式
- **插件（Plugin）**：一组相关的处理器和规则的集合

---

## 核心插件模块详解

所有核心代码都在 `src/plugins/kalulu/` 目录下。

### 入口文件 `__init__.py`

```python
from . import at_reply, random_chat, repeat
from .config import Config
```

这个文件做了两件事：
1. 导入三个子模块（`at_reply`、`random_chat`、`repeat`），触发它们的注册
2. 声明插件元数据（名称、描述、用法）

### 配置中心 `config.py`

这个文件定义了所有可配置的参数，用 Pydantic 的 `BaseModel` 来做类型验证。

**关键路径常量**：
```python
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
GROUPS_FILE = DATA_DIR / "groups.json"      # 群号存储
MEMES_DIR = DATA_DIR / "memes"              # 表情包图片目录
MEMORY_FILE = DATA_DIR / "memory.json"      # 长期记忆
KNOWLEDGE_DIR = DATA_DIR / "knowledge"      # RAG 知识库
```

**配置类 `Config`** 包含约 30+ 个配置项，每个都有：
- 类型标注（`bool`、`int`、`float`、`str`）
- 默认值
- 可选的范围限制（`ge=0.0, le=1.0` 表示 0 到 1 之间）

这些配置项会自动从 `.env.prod` 里读取，变量名就是 `.env.prod` 里的 key 转成小写。

---

### AI 对话引擎 `ai.py`

这是整个项目最核心的文件，负责和 AI API 通信。

#### 会话历史管理

```python
_histories: DefaultDict[str, ChatHistory] = defaultdict(list)
```

每个用户在每个群里都有独立的对话历史。key 是 `"群号:QQ号"`，value 是消息列表。

历史记录会被裁剪（`_trim_history`），只保留最近 N 轮对话（默认 10 轮 = 20 条消息）。

#### System Prompt 构建

每次调用 AI 之前，会构建一个 system prompt（系统提示词），包含三部分：

1. **人设 prompt**：来自 `persona.py`，定义帕朵的性格和说话风格
2. **RAG 知识**：从 `data/knowledge/` 检索相关内容
3. **长期记忆**：从 `data/memory.json` 加载该用户的记忆

```
system prompt = 人设 + RAG知识 + 用户记忆
```

#### API 调用

```python
async def _call_api(messages, *, max_tokens=None, model=None) -> str:
    payload = {
        "model": model or plugin_config.kalulu_ai_model,
        "messages": messages,
        "temperature": plugin_config.kalulu_ai_temperature,
    }
    # 小米 MiMo 特殊处理：禁用深度思考，避免 token 浪费在推理上
    if "xiaomimimo" in plugin_config.kalulu_ai_base_url:
        payload["max_completion_tokens"] = token_limit
        payload["thinking"] = {"type": "disabled"}
    else:
        payload["max_tokens"] = token_limit
```

**为什么要禁用"深度思考"？**

小米 MiMo 模型有一种"深度思考"模式，会先在内部推理一番再给出答案。但在群聊场景下，这会浪费大量 token（AI 的"字数"配额）在推理上，导致正式回复反而为空。所以要关掉。

#### 主函数 `chat()`

```python
async def chat(group_id, user_id, user_message, *, user_name="", bot=None, event=None, image_urls=None) -> str:
```

完整的调用流程：
1. 把用户消息加入会话历史
2. 构建 system prompt（人设 + RAG + 记忆）
3. 如果有图片，切换到视觉模型
4. 调用 AI API
5. 用 `polish_reply()` 润色回复
6. 把 AI 回复加入会话历史
7. 记录到长期记忆系统
8. 返回回复文本

#### 记忆提取

每聊 N 条消息（默认 8 条），会额外调用一次 AI，让它从对话中提炼值得长期记住的信息：

```
从 QQ 群对话里提取 1-2 条值得长期记住的精简信息，
比如对方昵称、喜好、正在做的事、群里的梗。
```

---

### 人设定义 `persona.py`

这个文件定义了帕朵的"性格"，通过 system prompt 告诉 AI 该怎么说话：

```
你在扮演群友「帕朵」，在一个熟人 QQ 群里水群。你是普通话痨网友，不是客服，不是 AI，不是角色扮演机器。

说话风格：
- 像真实群友：短、松、随意，有时几个字就行
- 会接梗、吐槽、敷衍、犯贱一点点都行，但别骂人
- 被 @ 且对方没事：回 怎么了？ / ？ / 嗯？ / 干啥？
- 别讲大道理，别科普，别像助手一样帮忙列步骤

标点规则：
- 只允许：，？！
- 禁止波浪号、省略号、括号动作、句号、冒号、markdown、列表

硬性禁止：
- （侧耳）(挠头) 这类描写
- 作为 AI / 助手 / 语言模型
```

**为什么这么写？**

因为 AI 默认会用一种"客服腔"说话（"好的，我来帮你..."、"希望对你有帮助"），这些 prompt 就是为了压制这种倾向，让它像一个真实的群友一样说话。

---

### 回复润色 `polish.py`

AI 生成的回复可能会带一些"AI 味"，这个模块负责把它洗掉。

#### 它做了什么？

1. **去掉 Markdown 标记**：`**加粗**` -> `加粗`、`` `代码` `` -> `代码`
2. **去掉列表格式**：`- xxx`、`1. xxx`
3. **去掉括号动作描写**：`（挠头）`、`(笑)` -- 真人不会这样说话
4. **去掉机器人话术**：`好的，`、`当然，`、`有什么可以帮你的吗`
5. **标点规范化**：
   - 禁止：波浪号、省略号、句号、冒号、引号
   - 只允许：逗号、问号、感叹号
   - `!` -> `！`、`?` -> `？`（中文标点）
6. **去重标点**：`，，，` -> `，`

如果清洗后为空，返回 `？` 作为兜底。

---

### 消息处理入口 `at_reply.py`

这是最核心的消息处理模块，负责"收到消息后怎么回复"。

#### 处理流程

```
收到群消息
    |
    +-- 记录群号（group_store）
    |
    +-- 提取用户文本内容
    |
    +-- 是空 @ ？-> 回复"怎么了？"
    |
    +-- 是问长相/照片？-> 发送机器人头像
    |
    +-- 尝试 AI 回复
    |   +-- 有图片？-> 尝试视觉识别
    |   +-- 识图失败？-> 发表情包兜底
    |   +-- AI 成功？-> 发送回复 + 可能追加表情包
    |   +-- AI 失败？-> 发"网卡了，再说一遍？"
    |
    +-- AI 不可用？-> 随机回复文字或表情包
```

#### 视觉识别流程

当消息包含图片时：

1. 检查是否是"纯表情包"（没有问文字）
   - 是 -> 按概率决定是否识图（默认 30%）
   - 否 -> 必须识图
2. 获取图片（通过 NapCat 的 `get_image` API 或 URL 下载）
3. 切换到视觉模型（`mimo-v2.5`）
4. 如果 AI 回复很弱（"看不清"、"没看懂"）-> 发表情包兜底

#### 表情包追加

AI 回复文字后，有 20% 的概率再追加一个表情包（`KALULU_AI_MEME_PROBABILITY=0.2`）。

---

### 随机冒泡 `random_chat.py`

这个模块让机器人定时在群里"冒泡"，制造活人感。

#### 工作原理

1. 使用 APScheduler 注册定时任务
2. 每隔 N 分钟（默认 10 分钟）检查一次
3. 按概率决定是否冒泡（默认 35%）
4. 随机选一个群
5. 按概率决定发文字还是发表情包（默认 50%）

#### 群号管理

机器人会自动记录它出现过的群（通过监听所有群消息）。这样随机冒泡就知道该往哪些群发消息。

```json
{
  "groups": [96928022, 213056772, 539106921, 655860576]
}
```

可以通过 `KALULU_ALLOWED_GROUPS` 配置项限制只在指定群里冒泡。

---

### 复读机 `repeat.py`

经典 QQ 群行为：当群里连续两个人发了同样的内容，第三个人（机器人）会跟着复读。

#### 工作原理

1. 监听所有群消息
2. 把消息标准化（去除多余空格等）
3. 生成消息的"指纹"（key），比如 `text:你好` 或 `image:xxx`
4. 如果连续两条消息的 key 相同，计数器 +1
5. 当计数器达到阈值（默认 2），触发复读

#### 支持复读的消息类型

- 文字消息
- 图片
- QQ 黄脸表情
- 商城表情
- 语音、视频
- JSON 消息、小程序分享

---

### 消息规则 `rules.py`

这个模块决定"这条消息要不要回复"。

#### 判断逻辑

```
收到消息
    |
    +-- 是机器人自己发的？-> 不回复
    |
    +-- @ 了别人但没 @ 机器人？-> 不回复（不要插嘴）
    |
    +-- 引用回复了别人但没 @ 机器人？-> 不回复
    |
    +-- @ 了机器人？-> 回复
    |
    +-- 被动回复模式（KALULU_PASSIVE_REPLY_ENABLED）：
        +-- "all"：所有消息都回复
        +-- "nickname"：提到昵称才回复
        +-- "random"：按概率随机回复
        +-- "combined"：提到昵称必回 + 其余按概率
```

---

### 消息解析 `message_context.py`

这个模块负责解析 QQ 消息的各个部分。

#### 核心功能

1. **`extract_user_content(event)`**：提取用户的文本内容
   - 去掉 @ 机器人的部分
   - 如果有媒体（图片/表情包），附加描述（如"发了张图：xxx"）

2. **`message_has_media(event)`**：判断消息是否包含媒体
   - 检查图片、表情、语音、视频等

3. **`message_has_sticker(event)`**：判断是否是表情包
   - QQ 黄脸表情、商城表情、动画表情

4. **`describe_message(event)`**：生成消息的文字描述
   - "发了表情包：动画表情"
   - "发了张图：图片"

---

### 视觉识别 `vision.py`

这个模块负责获取图片并转换成 AI 能理解的格式。

#### 图片获取流程

```
消息中有图片
    |
    +-- 有引用消息？-> 先从引用消息里找图片
    |
    +-- 从当前消息里找图片
    |
    +-- 对每张图片：
        +-- 尝试 NapCat 的 get_image API（获取 base64）
        +-- 失败？-> 尝试从 URL 下载
        +-- 还失败？-> 尝试从本地缓存读取
```

#### 为什么需要 base64？

AI API 接受图片的方式通常是 base64 编码（把图片文件转成一长串文字）。这个模块把图片转换成 `data:image/jpeg;base64,...` 格式的 URL，可以直接嵌入 API 请求。

---

### RAG 知识库 `knowledge.py`

RAG（Retrieval-Augmented Generation）的意思是"先检索，再生成"。

#### 工作原理

1. 加载 `data/knowledge/` 目录下的 `.md` 和 `.txt` 文件
2. 把文件内容切成小块（每块最多 320 字符）
3. 用户发消息时，用 bigram 匹配算法找到最相关的 3 块
4. 把这些内容注入到 system prompt 里

#### Bigram 匹配算法

这是一种简单的文本相似度算法：
1. 把查询文本拆成"二元组"（bigram），比如"你好世界" -> {"你好", "好世", "世界", "你", "好", "世", "界"}
2. 对每个知识块，统计有多少个 bigram 出现在其中
3. 匹配度 = 命中的 bigram 数 / 总 bigram 数
4. 按匹配度排序，取 top 3

**优点**：简单快速，不需要额外的向量数据库。
**缺点**：只能做字面匹配，不能理解语义。但对于群聊场景（关键词匹配）已经够用了。

#### 如何使用

往 `data/knowledge/` 里放 `.md` 或 `.txt` 文件就行。建议写：
- 群里的黑话、梗、常见话题
- 群友关系、谁是谁
- 帕朵的说话习惯补充
- 群规、活动、链接

改完文件**不用重启**，下次聊天会自动重新加载。

---

### 长期记忆 `memory.py`

这个模块让机器人"记住"每个群友。

#### 记忆内容

每个用户有以下记忆：

```json
{
  "user_id": 1344908013,
  "name": "卅",
  "notes": [
    "帕朵的开发者",
    "卅 喜欢耙耙柑"
  ],
  "recent_user": [
    "token是什么",
    "我去改一下",
    "有点蠢蠢的是这样的"
  ],
  "msg_count": 71
}
```

- `name`：用户的昵称
- `notes`：AI 提炼的长期记忆（每聊 8 条消息自动提炼一次）
- `recent_user`：最近说过的话（最多保留 20 条）
- `msg_count`：消息计数

#### 记忆注入

每次 AI 回复前，会把该用户的记忆注入到 system prompt 里：

```
【你记得的事】
对方 QQ：1344908013
正在跟你说话的人叫：卅
你以前记住的：
- 帕朵的开发者
- 卅 喜欢耙耙柑
对方最近说过：
- token是什么
- 我去改一下
```

#### 记忆提炼

每聊 N 条消息（默认 8 条），会额外调用一次 AI：

```
从 QQ 群对话里提取 1-2 条值得长期记住的精简信息，
比如对方昵称、喜好、正在做的事、群里的梗。
每行一条，不要解释。没有值得记的就只回复：无
```

提炼出的记忆会被合并到 `notes` 里，最多保留 15 条。

---

### 群号管理 `group_store.py`

这个模块负责记录机器人出现过的群。

#### 工作原理

1. 机器人在任何群里收到消息时，自动记录群号到 `data/groups.json`
2. 随机冒泡时，从已记录的群里随机选一个

#### API

- `remember_group(group_id)` -- 记录群号
- `load_groups()` -- 加载所有群号
- `get_target_groups(allowed)` -- 获取目标群号列表（如果指定了允许的群，就只返回交集）

---

### 文案模板 `replies.py`

这个模块定义了机器人在不同场景下可能发送的文字和表情。

#### 文案列表

- `AT_REPLY_TEXTS`：被 @ 且有文字时的回复模板
  ```python
  ["嗯？{text}", "{text}？", "啊这，{text}", "{text}，行吧", "草，{text}"]
  ```

- `IDLE_CHAT_TEXTS`：随机冒泡时的文字
  ```python
  ["有人吗", "好安静", "摸会儿鱼", "路过", "？", "今天咋这么静"]
  ```

- `QQ_FACE_IDS`：常用 QQ 黄脸表情 ID
  ```python
  [14, 21, 76, 96, 179, 180, 187, 201, 277, 289, 290, 294, 326, 338, 351]
  ```

#### 表情包选择

优先使用本地表情包（`data/memes/` 目录下的图片），如果目录为空则使用 QQ 黄脸表情。

---

## 数据文件说明

### `data/groups.json`

自动记录机器人出现过的群号：
```json
{
  "groups": [96928022, 213056772, 539106921, 655860576]
}
```

### `data/memory.json`

长期记忆存储，按 QQ 号记录每个用户的画像。目前记录了 15 个用户。

### `data/knowledge/`

RAG 知识库目录，存放 `.md` 或 `.txt` 文件。机器人聊天时会自动检索相关内容。

### `data/memes/`

本地表情包图片库，支持 jpg/png/gif/webp 格式。机器人会随机选择发送。

---

## 配置项详解

所有配置都在 `.env.prod` 里，以下是每个配置项的详细说明：

### 基础配置

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `HOST` | `127.0.0.1` | NoneBot2 监听地址 |
| `PORT` | `8090` | NoneBot2 监听端口 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `ONEBOT_ACCESS_TOKEN` | (空) | NapCat 连接用的 token |
| `SUPERUSERS` | `["1840203018"]` | 超级用户 QQ 号 |
| `NICKNAME` | `["帕朵菲莉丝", "帕朵"]` | 机器人昵称 |
| `KALULU_BOT_QQ_ID` | `1840203018` | 机器人自己的 QQ 号 |

### 功能开关

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `KALULU_AT_REPLY_ENABLED` | `true` | 是否启用 @ 回复 |
| `KALULU_RANDOM_CHAT_ENABLED` | `true` | 是否启用随机冒泡 |
| `KALULU_AI_ENABLED` | `true` | 是否启用 AI 对话 |
| `KALULU_VISION_ENABLED` | `true` | 是否启用视觉识别 |
| `KALULU_PASSIVE_REPLY_ENABLED` | `true` | 是否启用被动回复（不 @ 也回复） |
| `KALULU_REPEAT_ENABLED` | `true` | 是否启用复读机 |
| `KALULU_RAG_ENABLED` | `true` | 是否启用 RAG 知识库 |
| `KALULU_MEMORY_ENABLED` | `true` | 是否启用长期记忆 |

### 随机冒泡配置

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `KALULU_RANDOM_CHAT_INTERVAL_MINUTES` | `10` | 检查间隔（分钟） |
| `KALULU_RANDOM_CHAT_PROBABILITY` | `0.35` | 每次检查触发冒泡的概率 |
| `KALULU_MEME_PROBABILITY` | `0.5` | 发表情包 vs 发文字的概率 |
| `KALULU_ALLOWED_GROUPS` | `[]` | 允许冒泡的群号，空表示所有群 |

### AI 对话配置

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `KALULU_AI_API_KEY` | `sk-csv...` | AI API 密钥 |
| `KALULU_AI_BASE_URL` | `https://api.xiaomimimo.com/v1` | AI API 地址 |
| `KALULU_AI_MODEL` | `mimo-v2.5-pro` | 对话模型 |
| `KALULU_AI_MAX_HISTORY` | `10` | 保留最近几轮对话 |
| `KALULU_AI_MAX_TOKENS` | `180` | AI 回复最大 token 数 |
| `KALULU_AI_TEMPERATURE` | `0.95` | 回复随机性（0-2，越高越随机） |
| `KALULU_AI_TIMEOUT` | `60` | API 调用超时时间（秒） |
| `KALULU_AI_ONLY_WHEN_TEXT` | `true` | 空 @ 是否调用 AI |
| `KALULU_AI_MEME_PROBABILITY` | `0.2` | AI 回复后追加表情包的概率 |

### 视觉识别配置

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `KALULU_VISION_MODEL` | `mimo-v2.5` | 视觉模型 |
| `KALULU_VISION_FALLBACK_MEME_PROBABILITY` | `0.5` | 识图失败时发表情包的概率 |
| `KALULU_VISION_STICKER_PROBABILITY` | `0.3` | 收到表情包时尝试识图的概率 |

### 被动回复配置

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `KALULU_PASSIVE_REPLY_MODE` | `combined` | 被动回复模式 |
| `KALULU_PASSIVE_REPLY_PROBABILITY` | `0.6` | 随机回复的概率 |

### 复读机配置

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `KALULU_REPEAT_THRESHOLD` | `2` | 连续相同消息达到几次后复读 |
| `KALULU_REPEAT_MIN_LENGTH` | `1` | 复读的最短文字长度 |
| `KALULU_REPEAT_MAX_LENGTH` | `100` | 复读的最长文字长度 |

### RAG 知识库配置

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `KALULU_RAG_TOP_K` | `3` | 检索最相关的几条 |
| `KALULU_RAG_MAX_CHARS` | `600` | 注入 prompt 的最大字符数 |

### 长期记忆配置

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `KALULU_MEMORY_SUMMARIZE_EVERY` | `8` | 每聊几条消息提炼一次记忆 |
| `KALULU_MEMORY_MAX_NOTES` | `15` | 每个用户最多保留几条记忆 |
| `KALULU_MEMORY_RECENT_LIMIT` | `20` | 最近消息保留条数 |
| `KALULU_MEMORY_RECENT_PROMPT_COUNT` | `10` | 注入 prompt 时展示最近几条 |

---

## 如何自定义

### 修改人设

编辑 `src/plugins/kalulu/persona.py` 里的 `DEFAULT_SYSTEM_PROMPT`。

或者在 `.env.prod` 里设置 `KALULU_AI_SYSTEM_PROMPT`（会覆盖代码里的默认值）。

### 修改回复文案

编辑 `src/plugins/kalulu/replies.py`：
- `AT_REPLY_TEXTS` -- 被 @ 时的回复模板
- `IDLE_CHAT_TEXTS` -- 随机冒泡时的文字
- `QQ_FACE_IDS` -- QQ 黄脸表情 ID

### 添加表情包

把图片文件（jpg/png/gif/webp）放进 `data/memes/` 目录即可。

### 添加知识库

把 `.md` 或 `.txt` 文件放进 `data/knowledge/` 目录。改完不用重启。

### 切换 AI 模型

在 `.env.prod` 里修改：
- `KALULU_AI_BASE_URL` -- API 地址
- `KALULU_AI_MODEL` -- 模型名称
- `KALULU_AI_API_KEY` -- API 密钥

支持所有 OpenAI 兼容的 API（DeepSeek、小米 MiMo、OpenAI 等）。

### 调整行为参数

- 想让机器人更活跃：调高 `KALULU_RANDOM_CHAT_PROBABILITY` 和 `KALULU_PASSIVE_REPLY_PROBABILITY`
- 想让机器人话更多：调高 `KALULU_AI_MAX_TOKENS`
- 想让机器人更随机：调高 `KALULU_AI_TEMPERATURE`
- 想让机器人更像人：调高 `KALULU_AI_MEME_PROBABILITY`（多发表情包）

---

## 常见问题

### NapCat 连不上 NoneBot（403）

检查两边的 token 是否一致。`.env.prod` 里的 `ONEBOT_ACCESS_TOKEN` 要和 NapCat WebUI 里设置的一样。

### 随机冒泡不触发

机器人需要先在该群收到过至少一条消息（用于记录群号）。新群可以先 @ 一下或发句话。

### 图片发不出去

确认 `data/memes/` 里有图片，且 NapCat 有读取本地文件的权限。

### AI 回复为空

可能是"深度思考"占满了 token。检查是否使用了小米 MiMo，代码里已经自动禁用深度思考，但如果换了其他模型可能需要调整。

### 机器人太话痨

调低以下配置：
- `KALULU_RANDOM_CHAT_PROBABILITY` -- 降低冒泡频率
- `KALULU_PASSIVE_REPLY_PROBABILITY` -- 降低被动回复概率
- `KALULU_AI_MEME_PROBABILITY` -- 降低追加表情包概率

### 机器人太沉默

调高以上配置，或者把 `KALULU_PASSIVE_REPLY_MODE` 改成 `all`。

---

## 项目文件结构速查

```
d:\帕朵root\
|-- bot.py                          # 项目入口
|-- pyproject.toml                  # 项目配置 + NoneBot 插件声明
|-- .env / .env.prod                # 运行时配置
|-- requirements.txt                # Python 依赖
|-- README.md                       # 项目文档
|-- 开发笔记.md                      # 本文档
|
|-- data/
|   |-- groups.json                 # 群号记录
|   |-- memory.json                 # 长期记忆
|   |-- knowledge/                  # RAG 知识库
|   |   |-- README.md
|   |   +-- 示例-群聊.md
|   +-- memes/                      # 表情包图片
|
|-- src/plugins/kalulu/             # 核心插件
|   |-- __init__.py                 # 插件注册入口
|   |-- config.py                   # 配置中心
|   |-- ai.py                       # AI 对话引擎
|   |-- persona.py                  # 人设定义
|   |-- polish.py                   # 回复润色
|   |-- at_reply.py                 # @ 回复主处理器
|   |-- random_chat.py              # 随机冒泡
|   |-- repeat.py                   # 复读机
|   |-- rules.py                    # 消息匹配规则
|   |-- message_context.py          # 消息解析
|   |-- vision.py                   # 视觉识别
|   |-- knowledge.py                # RAG 知识检索
|   |-- memory.py                   # 长期记忆
|   |-- group_store.py              # 群号管理
|   +-- replies.py                  # 文案模板
|
|-- Nap/                            # NapCat Shell 版安装包
+-- Nap_node/                       # NapCat Node 版运行实例
```
