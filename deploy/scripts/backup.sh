#!/usr/bin/env bash
# CYINC 每日自动备份：site-data（posts.json + Content/）+ 上传目录（Docker 卷 uploads_data）
# 用法：手动执行 或 配置 crontab：
#   0 3 * * * /var/www/cyinc/deploy/scripts/backup.sh >> /var/log/cyinc-backup.log 2>&1
#
# 说明：备份到 /var/backups/cyinc/，保留最近 30 天
#       - site-data-YYYYMMDD.tar.gz：site-data/（posts.json + Content/）
#       - uploads-YYYYMMDD.tar.gz：上传目录卷（头像/论坛图/笔记图/贴纸等）
#       可用环境变量覆盖：RETENTION_DAYS、UPLOADS_RETENTION_DAYS、UPLOADS_VOLUME

set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/cyinc}"
SITE_DATA="${SITE_DATA:-$APP_ROOT/site-data}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/cyinc}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
UPLOADS_RETENTION_DAYS="${UPLOADS_RETENTION_DAYS:-$RETENTION_DAYS}"
UPLOADS_VOLUME="${UPLOADS_VOLUME:-}"

# 检查源数据是否存在
if [ ! -d "$SITE_DATA" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: site-data directory not found: $SITE_DATA" >&2
  exit 1
fi

# 检查是否有数据可备份
if [ ! -f "$SITE_DATA/data/posts.json" ] && ! ls "$SITE_DATA/Content/"*.html >/dev/null 2>&1; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: site-data is empty, skipping backup" >&2
  exit 0
fi

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d)
BACKUP_FILE="$BACKUP_DIR/site-data-${TIMESTAMP}.tar.gz"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] backing up $SITE_DATA -> $BACKUP_FILE"

if tar -czf "$BACKUP_FILE" -C "$(dirname "$SITE_DATA")" "$(basename "$SITE_DATA")" 2>/dev/null; then
  SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] backup done: $BACKUP_FILE ($SIZE)"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: backup failed" >&2
  exit 1
fi

# 清理超过保留天数的旧备份
DELETED=$(find "$BACKUP_DIR" -name "site-data-*.tar.gz" -mtime "+$RETENTION_DAYS" -delete -print 2>/dev/null | wc -l)
if [ "$DELETED" -gt 0 ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] cleaned $DELETED old backup(s)"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] site-data backup complete, $(ls "$BACKUP_DIR"/site-data-*.tar.gz 2>/dev/null | wc -l) files retained"
# ── 上传目录（Docker 卷：uploads_data）──
# 卷不存在/无 docker/无可用镜像时只告警跳过，不影响 site-data 备份结果
if ! command -v docker >/dev/null 2>&1; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: docker not found, skipping uploads backup"
else
  if [ -z "$UPLOADS_VOLUME" ]; then
    UPLOADS_VOLUME="$(docker volume ls --format '{{.Name}}' 2>/dev/null | grep -E 'uploads_data$' | head -n 1 || true)"
  fi

  if [ -z "$UPLOADS_VOLUME" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: uploads volume (*uploads_data) not found, skipping uploads backup"
  else
    UPLOADS_FILE="$BACKUP_DIR/uploads-${TIMESTAMP}.tar.gz"

    # 优先复用本机已有镜像，避免 ECS 无外网时拉取失败
    BACKUP_IMAGE=""
    for candidate in redis:7-alpine alpine busybox; do
      if docker image inspect "$candidate" >/dev/null 2>&1; then
        BACKUP_IMAGE="$candidate"
        break
      fi
    done

    if [ -z "$BACKUP_IMAGE" ]; then
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: no local image with tar (redis:7-alpine/alpine/busybox), skipping uploads backup"
    else
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] backing up volume $UPLOADS_VOLUME -> $UPLOADS_FILE"
      if docker run --rm --entrypoint tar \
        -v "$UPLOADS_VOLUME":/data:ro \
        -v "$BACKUP_DIR":/backup \
        "$BACKUP_IMAGE" -czf "/backup/uploads-${TIMESTAMP}.tar.gz" -C /data .; then
        SIZE=$(du -h "$UPLOADS_FILE" | cut -f1)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] uploads backup done: $UPLOADS_FILE ($SIZE)"
      else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: uploads backup failed" >&2
        exit 1
      fi

      DELETED=$(find "$BACKUP_DIR" -name "uploads-*.tar.gz" -mtime "+$UPLOADS_RETENTION_DAYS" -delete -print 2>/dev/null | wc -l)
      if [ "$DELETED" -gt 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] cleaned $DELETED old uploads backup(s)"
      fi
    fi
  fi
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] all done: site-data $(ls "$BACKUP_DIR"/site-data-*.tar.gz 2>/dev/null | wc -l) + uploads $(ls "$BACKUP_DIR"/uploads-*.tar.gz 2>/dev/null | wc -l) files retained"
