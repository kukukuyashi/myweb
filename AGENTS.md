# CYINC.LOG · AGENTS 铁律（所有 agent 会话必读）

> 本文件会被 AI 编码助手每次会话自动加载。修改前请三思，尤其下面的【部署铁律】。

## 🔴 部署铁律（违反会导致“笔记全变草稿”）

背景：运行时数据（文章索引 posts.json + 文章正文 Content/*.html）与前端构建产物是两回事。历史上多次因为把两者混在同一目录，被 rsync --delete 覆盖，导致笔记全部变回草稿。已用“物理隔离”根治。

现在的架构（生产 ECS）：
- 运行时数据住在 `/var/www/cyinc/site-data/`（`data/posts.json` + `Content/`），与前端部署目录 `/var/www/cyinc/myweb/` 物理隔离。
- 后端靠环境变量 `SITE_DATA_ROOT=/data/site` 读写（compose 挂载 `./site-data:/data/site`）。
- Nginx：`location ^~ /myweb/Content/` 与 `location = /myweb/data/posts.json` 用 `alias` 指向 `site-data/`。

上线只允许这一条（前端+后端通用）：
```
cd /var/www/cyinc && bash deploy/scripts/ecs-update.sh
```
后端有改动时再补重建容器：
```
docker-compose -f docker-compose.prod.yml stop api
docker-compose -f docker-compose.prod.yml rm -f api
docker-compose -f docker-compose.prod.yml up -d --build api
```

> ⚠️ 兼容性：本服务器装的是老版 docker-compose（v1，带横杠），没有 docker compose（v2，空格）。上线命令一律用横杠版 docker-compose。ecs-update.sh 已内置自动探测（v1/v2 都兼容），改脚本时别写死成空格版 docker compose。

绝对禁止：
- ❌ 不要手敲 `rsync -a --delete docs/ myweb/`（尤其不带 exclude）——会删掉/覆盖运行时数据。
- ❌ 不要把 posts.json / Content/ 写回 myweb/。
- ✅ 如必须手动 rsync，必带：`--exclude=data/posts.json --exclude=Content/ --exclude=uploads/`。

如果笔记又变草稿了（恢复命令）：从 md 源重发（重建 HTML + 补回 posts.json）：
```
docker exec cyinc_api_1 python -c "
from app.services.notes_store import list_notes, assert_note_abs
from app.services.notes_markdown import parse_frontmatter
from app.services.notes_publish import resolve_post_meta, publish_markdown_file
from app.services.posts_catalog import load_posts
posts=load_posts(); pub={p.get('file') for p in posts}
ok=[]
for n in list_notes():
    rel=n['relPath']; p=assert_note_abs(rel)
    meta,body=parse_frontmatter(p.read_text(encoding='utf-8'))
    f=resolve_post_meta(meta=meta,body=body,md_path=p,posts=posts)['file']
    if f in pub: continue
    publish_markdown_file(rel); ok.append(f)
print('republished', len(ok))
from app.services.posts_catalog import load_posts as lp
print('posts after', len(lp()))
"
```

备份建议（site-data 是最宝贵的目录）：
```
# 手动备份
bash /var/www/cyinc/deploy/scripts/backup.sh

# 自动每日备份（ECS 上执行一次即可）：
# crontab -e  添加：
# 0 3 * * * /var/www/cyinc/deploy/scripts/backup.sh >> /var/log/cyinc-backup.log 2>&1
```

## 代码提交约束
- 只 `git add <具体文件> docs`，绝不 `git add -A`。
- 不提交：`agent.md`、`笔记/`、`uploads/`、`*.tar.gz`/`*.zip`、`.env`、`site-data/`。

## 项目速查
- 前端 Vue3+Vite（构建到 `docs/`，base `/myweb/`）；后端 FastAPI+MySQL+Redis。
- 主区 `/myweb/app/*`；管理台 `/myweb/admin/*`（仪表盘/笔记/机器人/数据管理）。
- 本地 Windows/PowerShell；生产阿里云 ECS Docker，域名 `cyinc.ink`，容器 `cyinc_api_1`/`cyinc_redis_1`。