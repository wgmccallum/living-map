#!/bin/bash
# Restore the database to the seed snapshot.
# Use this to reset after collaborators have made changes.
#
# Usage:
#   ./restore.sh           # Restore from living_map.seed.db
#   ./restore.sh --backup  # Save current DB before restoring

set -e
cd "$(dirname "$0")"

if [ ! -f living_map.seed.db ]; then
  echo "Error: No snapshot found (living_map.seed.db). Run deploy.sh first to create one."
  exit 1
fi

if [ "$1" = "--backup" ]; then
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  cp living_map.db "living_map.backup_${TIMESTAMP}.db"
  echo "Backed up current DB → living_map.backup_${TIMESTAMP}.db"
fi

cp living_map.seed.db living_map.db
echo "Database restored from snapshot."
echo "Restart the server to pick up changes."
