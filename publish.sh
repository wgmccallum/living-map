#!/bin/bash
# Publish local DB to production.
# Copies living_map.db → living_map.live.db, commits, pushes.
# Railway redeploys automatically on push.
#
# Usage:
#   ./publish.sh                       # Interactive: shows diff, asks before commit
#   ./publish.sh -m "added KCs for X"  # Custom commit message
#   ./publish.sh --dry-run             # Show what would happen, no changes
#   ./publish.sh --yes                 # Skip confirmation prompt

set -e

DRY_RUN=false
YES=false
MSG=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --yes|-y) YES=true; shift ;;
    -m) MSG="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

cd "$(dirname "$0")"

if [ ! -f living_map.db ]; then
  echo "Error: living_map.db not found"
  exit 1
fi

if [ ! -f living_map.live.db ]; then
  echo "Note: living_map.live.db doesn't exist yet — this will be the first publish."
fi

# SQLite runs in WAL mode: recent commits live in living_map.db-wal, so a plain
# file copy/compare of living_map.db alone would miss them. Flush the WAL into the
# main file first so the cmp below, the size readout, and the copy are all current.
sqlite3 living_map.db 'PRAGMA wal_checkpoint(TRUNCATE);' >/dev/null

# Nothing-to-do check
if [ -f living_map.live.db ] && cmp -s living_map.db living_map.live.db; then
  echo "living_map.db and living_map.live.db are already identical — nothing to publish."
  exit 0
fi

# Summary
echo "=== Publish summary ==="
printf "  Local size:  %s bytes\n" "$(stat -f%z living_map.db)"
if [ -f living_map.live.db ]; then
  printf "  Live size:   %s bytes\n" "$(stat -f%z living_map.live.db)"
fi
echo ""
echo "  Row counts (live → local):"
for tbl in knowledge_components schemas prerequisite_edges annotations; do
  local_n=$(sqlite3 living_map.db "SELECT COUNT(*) FROM $tbl" 2>/dev/null || echo "?")
  if [ -f living_map.live.db ]; then
    live_n=$(sqlite3 living_map.live.db "SELECT COUNT(*) FROM $tbl" 2>/dev/null || echo "?")
  else
    live_n="—"
  fi
  printf "    %-25s %5s → %5s\n" "$tbl" "$live_n" "$local_n"
done

if [ "$DRY_RUN" = true ]; then
  echo ""
  echo "(dry run — no changes made)"
  exit 0
fi

# Confirm
if [ "$YES" = false ]; then
  echo ""
  read -p "Proceed with publish (copy → commit → push)? [y/N] " ans
  if [[ "$ans" != "y" && "$ans" != "Y" ]]; then
    echo "Aborted."
    exit 0
  fi
fi

# Default commit message
if [ -z "$MSG" ]; then
  MSG="publish: update live DB snapshot ($(date +%Y-%m-%d))"
fi

# Do it. `git commit <file>` commits only that file, ignoring anything else
# already staged — keeps the publish surgical.
# WAL-safe copy: sqlite3 .backup produces an atomic, consistent single-file copy
# even if the server is running. Clear any stale sidecar files on the target first.
rm -f living_map.live.db-wal living_map.live.db-shm
sqlite3 living_map.db ".backup 'living_map.live.db'"
git add living_map.live.db
git commit living_map.live.db -m "$MSG"
git push

echo ""
echo "Published. Railway will redeploy from the new commit."
