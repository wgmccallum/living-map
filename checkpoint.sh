#!/bin/bash
# Create, list, and restore timestamped checkpoints of the working DB.
# Unlike snapshot.sh (which maintains the single seed used by restore.sh),
# checkpoints are cheap, keep-many backups for mid-editing-session safety.
#
# Usage:
#   ./checkpoint.sh [label]            # Create living_map.db.bak_<label>_<timestamp>
#   ./checkpoint.sh --list             # List existing checkpoints
#   ./checkpoint.sh --restore <file>   # Restore working DB from a checkpoint

set -e
cd "$(dirname "$0")"

usage() { sed -n '2,9p' "$0"; }

server_running() {
  lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1
}

row_counts() {
  local db=$1
  for tbl in knowledge_components schemas prerequisite_edges; do
    n=$(sqlite3 "$db" "SELECT COUNT(*) FROM $tbl" 2>/dev/null || echo "?")
    printf "    %-25s %5s\n" "$tbl" "$n"
  done
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;

  --list)
    shopt -s nullglob
    files=()
    for f in living_map.db.bak_*; do
      [[ "$f" == *-wal || "$f" == *-shm ]] && continue
      files+=("$f")
    done
    if [ ${#files[@]} -eq 0 ]; then
      echo "No checkpoints found."
      exit 0
    fi
    echo "=== Checkpoints (oldest first) ==="
    ls -lt -r "${files[@]}" | awk '{printf "  %s %s %s  %s\n", $6, $7, $8, $9}'
    exit 0
    ;;

  --restore)
    src="${2:-}"
    if [ -z "$src" ]; then
      echo "Error: --restore needs a checkpoint file. Use --list to see them."
      exit 1
    fi
    if [ ! -f "$src" ]; then
      echo "Error: $src not found."
      exit 1
    fi
    if server_running; then
      echo "Error: something is listening on port 8000 — stop the server before restoring,"
      echo "otherwise it will keep writing to the old database state."
      exit 1
    fi
    echo "Restoring living_map.db from $src"
    echo ""
    echo "  Row counts in checkpoint:"
    row_counts "$src"
    echo ""
    read -p "Overwrite working DB with this checkpoint? [y/N] " ans
    if [[ "$ans" != "y" && "$ans" != "Y" ]]; then
      echo "Aborted."
      exit 0
    fi
    # Safety net: checkpoint the current state first (WAL-safe)
    safety="living_map.db.bak_prerestore_$(date +%Y%m%d_%H%M%S)"
    sqlite3 living_map.db ".backup '$safety'"
    echo "Saved current state → $safety"
    # Replace the DB; stale -wal/-shm sidecars would corrupt the restored copy
    rm -f living_map.db-wal living_map.db-shm
    cp "$src" living_map.db
    echo "Working DB restored from $src. Restart the server to pick up changes."
    exit 0
    ;;

  --*)
    echo "Unknown option: $1"
    usage
    exit 1
    ;;
esac

# Default: create a checkpoint
label="${1:-checkpoint}"
if [[ ! "$label" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "Error: label must be alphanumeric (plus . _ -), got: $label"
  exit 1
fi
dest="living_map.db.bak_${label}_$(date +%Y%m%d_%H%M%S)"

if [ ! -f living_map.db ]; then
  echo "Error: living_map.db not found"
  exit 1
fi

# sqlite3 .backup is WAL-safe and consistent even while the server is running
sqlite3 living_map.db ".backup '$dest'"
# Convert the checkpoint to rollback-journal mode so it stays a single file
# (WAL-mode files sprout -wal/-shm sidecars every time they're opened)
sqlite3 "$dest" "PRAGMA journal_mode=DELETE;" >/dev/null
rm -f "$dest-wal" "$dest-shm"
echo "Checkpoint created: $dest"
echo ""
echo "  Row counts:"
row_counts "$dest"
echo ""
echo "Restore later with: ./checkpoint.sh --restore $dest"
