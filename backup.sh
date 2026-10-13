#!/bin/sh
# Daily backup: consistent database copy + all uploads, kept 14 days.
# Optional off-site copy: install rclone, run `rclone config`, then set REMOTE (for example b2:spicy-backups).
set -e
cd "$(dirname "$0")/.."
STAMP=$(date +%Y%m%d-%H%M%S)
mkdir -p backups
sqlite3 data/spicy.db ".backup 'backups/spicy-$STAMP.db'"
tar -czf "backups/spicy-$STAMP.tar.gz" -C backups "spicy-$STAMP.db" -C ../data media
rm -f "backups/spicy-$STAMP.db"
find backups -name 'spicy-*.tar.gz' -mtime +14 -delete
if [ -n "$REMOTE" ] && command -v rclone >/dev/null; then rclone copy backups "$REMOTE" --include 'spicy-*.tar.gz'; fi
echo "backup ok: backups/spicy-$STAMP.tar.gz"
