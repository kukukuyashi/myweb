#!/usr/bin/env bash
# CYINC site-data 每日自动备份
# 用法：手动执行 或 配置 crontab：
#   0 3 * * * /var/www/cyinc/deploy/scripts/backup.sh >> /var/log/cyinc-backup.log 2>&1
#
# 说明：备份 site-data/（posts.json + Content/）到 /var/backups/cyinc/，
#       保留最近 30 天，文件名格式：site-data-YYYYMMDD.tar.gz

set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/cyinc}"
SITE_DATA="${SITE_DATA:-$APP_ROOT/site-data}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/cyinc}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

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

echo "[$(date '+%Y-%m-%d %H:%M:%S')] backup complete, $(ls "$BACKUP_DIR"/site-data-*.tar.gz 2>/dev/null | wc -l) files retained"