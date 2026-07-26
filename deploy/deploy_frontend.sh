#!/usr/bin/env bash
# Deploy the BTB website (BTB_Website) to the live server.
#
#   1. Validate a local production build (catches errors before touching prod).
#   2. Sync the source to the server (minus node_modules / dist).
#   3. Rebuild ON the server, preserving the admin-edited interviews.json, and
#      roll back to the previous dist if the build fails.
#
# Config via env vars (defaults target the live box):
#   BTB_HOST=root@64.83.14.229   BTB_SSH_KEY=~/.ssh/btb_deploy
#
# Usage:  bash deploy/deploy_frontend.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
KEY="${BTB_SSH_KEY:-$HOME/.ssh/btb_deploy}"
HOST="${BTB_HOST:-root@64.83.14.229}"
REMOTE_DIR="/opt/btb/BTB_Website"
SSH=(ssh -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new "$HOST")

echo "== [1/3] local build check =="
cd "$ROOT/BTB_Website"
npm run build >/dev/null
test -f dist/index.html
echo "   local build OK"

echo "== [2/3] sync source -> $HOST:$REMOTE_DIR (keeping server interviews.json) =="
tar --exclude=node_modules --exclude=dist -czf - . \
  | "${SSH[@]}" "cd '$REMOTE_DIR' && cp -f src/data/interviews.json /tmp/btb_iv.json 2>/dev/null; tar -xzf - ; cp -f /tmp/btb_iv.json src/data/interviews.json 2>/dev/null; rm -f /tmp/btb_iv.json; true"

echo "== [3/3] build on server (zero-downtime swap) =="
"${SSH[@]}" 'bash -s' <<REMOTE
set -e
cd '$REMOTE_DIR'
npm install --no-audit --no-fund --silent
rm -rf dist.new dist.old
# Build into a fresh dir so the live dist keeps serving during the whole build;
# swap in only on success (millisecond window), so crawlers never hit an empty dist.
if npm run build -- --outDir dist.new >/tmp/btb_build.log 2>&1 && [ -f dist.new/index.html ]; then
  [ -d dist ] && mv dist dist.old
  mv dist.new dist
  rm -rf dist.old
  echo "FRONTEND_DEPLOYED"
else
  echo "BUILD_FAILED — live site untouched"; tail -40 /tmp/btb_build.log
  rm -rf dist.new
  exit 1
fi
REMOTE

echo "Done -> https://thebtbpodcast.com/"
