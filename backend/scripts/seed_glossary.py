"""Seed glossary terms for CYINC.LOG.

Run on ECS (idempotent, safe to re-run):
    docker exec -i cyinc_api_1 python -m scripts.seed_glossary
"""

from app.core.db import Base, SessionLocal, engine
from app.models.glossary import GlossaryTerm

TERMS = [
    # ============ 网络基础 ============
    ("DNS解析", "DNS,域名系统", "把域名（网址）翻译成服务器 IP 地址的过程，就像电话簿查名字找号码。", "网络基础"),
    ("HTTP", "超文本传输协议", "浏览器和服务器之间传输网页数据的协议，默认端口 80。", "网络基础"),
    ("HTTPS", "HTTP over TLS", "加密的 HTTP，通过 SSL/TLS 证书对通信内容加密，防止被窃听或篡改，默认端口 443。", "网络基础"),
    ("SSL/TLS", "安全套接层,传输层安全", "加密网络通信的协议，确保数据在传输过程中不被窃取或篡改，是 HTTPS 的基础。", "网络基础"),
    ("IP地址", "IP", "互联网协议地址，每台联网设备的唯一标识，如 8.138.238.171。", "网络基础"),
    ("域名", "", "网站的可读名称（如 cyinc.ink），DNS 将其解析为 IP 地址。", "网络基础"),
    ("端口", "Port", "计算机上用于区分不同服务的编号，如 80=HTTP、443=HTTPS、8000=API。", "网络基础"),
    ("防火墙", "安全组", "控制网络流量进出的安全规则，阿里云安全组就是一台虚拟防火墙。", "网络基础"),

    # ============ 服务器 / 部署 ============
    ("Nginx", "", "高性能 Web 服务器和反向代理，常用作静态文件服务、HTTPS 卸载、负载均衡。", "服务器/部署"),
    ("Docker", "", "容器化技术，把应用及其依赖打包成标准单元，实现一次构建、到处运行。", "服务器/部署"),
    ("容器", "Container", "Docker 创建的轻量级虚拟运行环境，每个容器包含应用及其依赖。", "服务器/部署"),
    ("Docker Compose", "compose", "定义和运行多容器应用的工具，通过 YAML 文件一键启动所有服务。", "服务器/部署"),
    ("镜像", "Image", "Docker 容器的只读模板，包含运行应用所需的代码、运行时和库。", "服务器/部署"),
    ("ECS", "云服务器,弹性云服务器", "阿里云 Elastic Compute Service，即云上的虚拟服务器，本站部署所在。", "服务器/部署"),
    ("反向代理", "Reverse Proxy", "服务器端代理，接收客户端请求并转发给后端服务，Nginx 即扮演此角色。", "服务器/部署"),
    ("负载均衡", "Load Balance", "将网络流量分发到多台服务器，提高可用性和性能。", "服务器/部署"),
    ("CDN", "内容分发网络", "将静态资源缓存到全球多个节点，用户从最近节点获取，加速访问。", "服务器/部署"),
    ("Let's Encrypt", "Certbot", "免费、自动化的 SSL 证书颁发机构，本项目 HTTPS 证书的来源。", "服务器/部署"),
    ("SSL证书", "TLS证书,数字证书", "用于验证网站身份并启用 HTTPS 加密的数字凭证。", "服务器/部署"),
    ("Uvicorn", "", "基于 ASGI 的高性能 Python Web 服务器，本项目在容器内用它运行 FastAPI。", "服务器/部署"),

    # ============ 后端 ============
    ("FastAPI", "", "高性能 Python Web 框架，支持异步、自动生成接口文档，本项目后端框架。", "后端"),
    ("API", "应用程序接口", "应用程序编程接口，定义不同软件组件之间如何通信。", "后端"),
    ("RESTful", "REST", "一种 API 设计风格，用 HTTP 方法（GET/POST/PATCH/DELETE）操作资源。", "后端"),
    ("JSON", "", "轻量级数据交换格式，便于人读和机器解析，API 接口常用。", "后端"),
    ("SQL", "结构化查询语言", "操作关系型数据库的标准语言，包括增删改查。", "后端"),
    ("ORM", "对象关系映射", "把数据库表映射为编程语言中的对象（如 SQLAlchemy），免写原生 SQL。", "后端"),
    ("MySQL", "", "最流行的开源关系型数据库，本项目的持久化存储。", "后端"),
    ("Redis", "", "内存数据库，用作缓存和消息队列，本项目存储会话与验证码。", "后端"),
    ("外键", "外键约束", "数据库表之间的关联约束，确保引用完整（如帖子引用的用户必须存在）。", "后端"),
    ("索引", "数据库索引", "加速数据库查询的数据结构，类似书的目录。", "后端"),
    ("事务", "数据库事务", "一组数据库操作要么全部成功、要么全部回滚，保证数据一致性。", "后端"),
    ("CORS", "跨域资源共享", "浏览器安全机制，控制不同域名之间的资源请求权限。", "后端"),
    ("JWT", "JSON Web Token", "基于 JSON 的身份认证令牌，本项目管理员和论坛用户登录后都使用它。", "后端"),
    ("中间件", "Middleware", "在请求到达路由前后执行的代码，如日志、认证、CORS 处理。", "后端"),
    ("SMTP", "简单邮件传输协议", "发送电子邮件的协议，本项目用于发送验证码和通知邮件。", "后端"),

    # ============ 前端 ============
    ("Vue.js", "Vue,Vue3", "渐进式 JavaScript 前端框架，采用组件化开发，本项目前端框架。", "前端"),
    ("Vite", "", "新一代前端构建工具，开发时热更新极速，生产构建快速。", "前端"),
    ("DOM", "文档对象模型", "浏览器把 HTML 解析成的树形结构，JavaScript 通过操作 DOM 改变页面。", "前端"),
    ("SPA", "单页应用", "整个网站只有一个 HTML 页面，通过 JS 动态切换视图。", "前端"),
    ("SSR", "服务端渲染", "服务器生成完整 HTML 再发给浏览器，首屏加载快、利于 SEO。", "前端"),
    ("毛玻璃效果", "Glassmorphism,毛玻璃", "通过背景模糊实现半透明磨砂玻璃质感的 UI 风格。", "前端"),
    ("响应式设计", "Responsive,响应式", "网站自适应手机/平板/电脑等不同屏幕，通过 CSS 媒体查询实现。", "前端"),
    ("预渲染", "Prerender", "构建时提前生成静态 HTML，加快首屏加载，本项目博客使用。", "前端"),
    ("WebSocket", "", "浏览器与服务器之间的全双工（双向）实时通信协议。", "前端"),

    # ============ 安全 ============
    ("SQL注入", "SQL Injection", "攻击者通过输入恶意 SQL 操纵数据库的漏洞，用 ORM 可有效防止。", "安全"),
    ("XSS", "跨站脚本攻击", "攻击者向网站注入恶意脚本，窃取用户信息或篡改页面。", "安全"),
    ("CSRF", "跨站请求伪造", "诱导用户在已登录状态下执行非自愿操作的攻击方式。", "安全"),

    # ============ 工具 / 流程 ============
    ("Git", "", "分布式版本控制系统，记录代码变更历史，支持多人协作。", "工具/流程"),
    ("GitHub", "", "基于 Git 的代码托管平台，提供 Issues、PR、Actions 等协作功能。", "工具/流程"),
    ("GitHub Actions", "GHA", "GitHub 内置的 CI/CD 自动化工具，推送代码可自动构建/测试/部署。", "工具/流程"),
    ("CI/CD", "持续集成,持续部署", "自动化构建、测试、部署的开发实践，推送代码即自动上线。", "工具/流程"),
    ("pip", "", "Python 的包管理器，安装和管理 Python 第三方库。", "工具/流程"),
    ("npm", "", "Node.js 的包管理器，安装和管理 JavaScript 第三方库。", "工具/流程"),
    ("环境变量", "env", "操作系统级别的配置参数，用于在不同环境（开发/生产）下配置应用行为。", "工具/流程"),
    ("ASGI", "WSGI", "Python Web 服务器与应用之间的接口标准，ASGI 支持异步，WSGI 仅同步。", "工具/流程"),
]


def seed_glossary():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seen = {r.term for r in db.query(GlossaryTerm).all()}
        added = 0
        skipped = 0
        for term, aliases, definition, category in TERMS:
            if term in seen:
                skipped += 1
                continue
            db.add(GlossaryTerm(
                term=term,
                aliases=aliases or None,
                definition=definition,
                category=category or None,
            ))
            seen.add(term)
            added += 1
        db.commit()
        print(f"glossary seeded: {added} added, {skipped} skipped (already existed)")
        print(f"total terms now: {db.query(GlossaryTerm).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_glossary()