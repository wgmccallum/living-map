#!/bin/bash
# Refresh the seed snapshot used by ./restore.sh.
# Copies living_map.db → living_map.seed.db with safety checks.
#
# Usage:
#   ./snapshot.sh             # Interactive: shows current seed age, asks before overwriting
#   ./snapshot.sh --yes       # Skip confirmation
#   ./snapshot.sh --dry-run   # Show what would happen, no changes

set -e

DRY_RUN=false
YES=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --yes|-y) YES=true; shift ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

cd "$(dirname "$0")"

if [ ! -f living_map.db ]; then
  echo "Error: living_map.db not found"
  exit 1
fi

# Warn if server is still running — snapshotting a DB with open writes is risky
if lsof -nP -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Warning: something is listening on port 8000 — the server may still be running."
  echo "Snapshotting an active DB can capture a partial write. Stop the server first."
  if [ "$YES" = false ]; then
    read -p "Continue anyway? [y/N] " ans
    if [[ "$ans" != "y" && "$ans" != "Y" ]]; then
      echo "Aborted."
      exit 0
    fi
  fi
fi

# Summary
echo "=== Snapshot summary ==="
if [ -f living_map.seed.db ]; then
  seed_date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" living_map.seed.db)
  seed_age_days=$(( ($(date +%s) - $(stat -f %m living_map.seed.db)) / 86400 ))
  printf "  Current seed: %s (%d days old)\n" "$seed_date" "$seed_age_days"
else
  echo "  Current seed: none (this will be the first snapshot)"
fi
echo ""
echo "  Row counts (seed → new):"
for tbl in knowledge_components schemas prerequisite_edges annotations; do
  new_n=$(sqlite3 living_map.db "SELECT COUNT(*) FROM $tbl" 2>/dev/null || echo "?")
  if [ -f living_map.seed.db ]; then
    seed_n=$(sqlite3 living_map.seed.db "SELECT COUNT(*) FROM $tbl" 2>/dev/null || echo "?")
  else
    seed_n="—"
  fi
  printf "    %-25s %5s → %5s\n" "$tbl" "$seed_n" "$new_n"
done

if [ "$DRY_RUN" = true ]; then
  echo ""
  echo "(dry run — no changes made)"
  exit 0
fi

# Confirm
if [ "$YES" = false ]; then
  echo ""
  read -p "Overwrite seed with current working DB? [y/N] " ans
  if [[ "$ans" != "y" && "$ans" != "Y" ]]; then
    echo "Aborted."
    exit 0
  fi
fi

cp living_map.db living_map.seed.db
echo ""
echo "Seed refreshed. ./restore.sh will now roll back to this state."
