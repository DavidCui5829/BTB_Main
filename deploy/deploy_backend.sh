#!/usr/bin/env bash
# Deploy the BTB AI backend (BTB_AI) to the live server and restart it.
#
# Syncs the app code but preserves the server's .env (API keys, model,
# admin token) and its built vectorstore. Restarts btb-backend and waits for
# the health check.
#
# Config via env vars (defaults target the live box):
#   BTB_HOST=root@64.83.14.229   BTB_SSH_KEY=~/.ssh/btb_deploy
#
# Usage:  bash deploy/deploy_backend.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
KEY="${BTB_SSH_KEY:-$HOME/.ssh/btb_deploy}"
HOST="${BTB_HOST:-root@64.83.14.229}"
REMOTE_DIR="/opt/btb/BTB_AI"
SSH=(ssh -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new "$HOST")

echo "== [1/2] sync app code -> $HOST:$REMOTE_DIR (keeping server .env + vectorstore) =="
cd "$ROOT/BTB_AI"
tar --exclude=.venv --exclude=__pycache__ --exclude='*.pyc' \
    --exclude=vectorstore --exclude=.env -czf - . \
  | "${SSH[@]}" "cd '$REMOTE_DIR' && cp -f .env /tmp/btb_ai_env 2>/dev/null; tar -xzf - ; cp -f /tmp/btb_ai_env .env 2>/dev/null; rm -f /tmp/btb_ai_env; true"

echo "== [2/2] restart + health check =="
"${SSH[@]}" 'bash -s' <<'REMOTE'
set -e
systemctl restart btb-backend
for i in $(seq 1 30); do
  if curl -sf -m 3 http://127.0.0.1:8000/health >/dev/null; then
    echo "BACKEND_DEPLOYED (healthy)"; exit 0
  fi
  sleep 2
done
echo "BACKEND: health check timed out"
systemctl status btb-backend --no-pager | tail -20
exit 1
REMOTE

echo "Done -> https://thebtbpodcast.com/api/health"
