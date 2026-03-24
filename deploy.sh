#!/bin/bash
# Deploy script for Living Map
# Builds the frontend and starts the server on a single port.
#
# Usage:
#   ./deploy.sh                       # Build + run on port 8000 (edits your DB)
#   ./deploy.sh --sandbox             # Run against a temporary copy (your DB is safe)
#   ./deploy.sh --sandbox --tunnel    # Same + open a public URL via cloudflared
#   ./deploy.sh --port 3000           # Custom port
#   ./deploy.sh --skip-build          # Run without rebuilding frontend
#   ./deploy.sh --rebuild             # Rebuild frontend + restart sandbox + tunnel

set -e

PORT=8000
SKIP_BUILD=false
SANDBOX=false
TUNNEL=false
REBUILD=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --port) PORT="$2"; shift 2 ;;
    --skip-build) SKIP_BUILD=true; shift ;;
    --sandbox) SANDBOX=true; shift ;;
    --tunnel) TUNNEL=true; shift ;;
    --rebuild) REBUILD=true; SANDBOX=true; TUNNEL=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# If rebuilding, kill any existing server and tunnel on the port
if [ "$REBUILD" = true ]; then
  echo "Rebuilding: stopping existing server and tunnel..."
  lsof -ti:$PORT 2>/dev/null | xargs kill 2>/dev/null || true
  pkill -f cloudflared 2>/dev/null || true
  sleep 1
fi

cd "$(dirname "$0")"

# Build frontend if needed
if [ "$SKIP_BUILD" = false ]; then
  echo "Building frontend..."
  cd frontend
  npm install --silent
  npm run build
  cd ..
  echo "Frontend built → living_map/static/"
fi

# Snapshot the database if no snapshot exists yet
if [ ! -f living_map.seed.db ]; then
  echo "Creating database snapshot → living_map.seed.db"
  cp living_map.db living_map.seed.db
fi

# Determine which DB to use
DB_PATH="living_map.db"
if [ "$SANDBOX" = true ]; then
  SANDBOX_DIR="sandboxes"
  mkdir -p "$SANDBOX_DIR"
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  DB_PATH="${SANDBOX_DIR}/sandbox_${TIMESTAMP}.db"
  cp living_map.db "$DB_PATH"
  echo "Sandbox mode: working on copy at $DB_PATH"
  echo "Your living_map.db is untouched."
fi

# Start tunnel in background if requested
if [ "$TUNNEL" = true ]; then
  if ! command -v cloudflared &> /dev/null; then
    echo "Error: cloudflared not installed. Run: brew install cloudflared"
    exit 1
  fi
  echo "Starting tunnel..."
  cloudflared tunnel --url "http://localhost:$PORT" > /tmp/cloudflared.log 2>&1 &
  TUNNEL_PID=$!
  sleep 8
  TUNNEL_URL=$(grep -o 'https://[^ ]*trycloudflare.com' /tmp/cloudflared.log | head -1)
  echo ""
  echo "═══════════════════════════════════════════════════════"
  echo "  Public URL: $TUNNEL_URL"
  echo "  Share this with your collaborators!"
  echo "═══════════════════════════════════════════════════════"
  echo ""
  # Clean up tunnel on exit
  trap "kill $TUNNEL_PID 2>/dev/null; echo 'Tunnel stopped.'" EXIT
fi

echo "Starting Living Map on http://0.0.0.0:$PORT"
echo "Press Ctrl+C to stop"
echo ""

python3 -c "
import uvicorn
from living_map.app import app
app.state.db_path = '$DB_PATH'
uvicorn.run(app, host='0.0.0.0', port=$PORT)
"
