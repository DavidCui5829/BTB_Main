#!/bin/bash
# One-shot BTB deployment for CentOS Stream 9.
# Expects /root/btb_deploy.tar.gz and /root/btb.env.extra to exist.
# Writes progress to /root/btb_deploy.log; last line DEPLOY_OK / DEPLOY_FAILED.
set -euo pipefail
exec > /root/btb_deploy.log 2>&1

trap 'echo DEPLOY_FAILED' ERR

echo "=== [1/8] node 20 + swap ==="
if ! node --version 2>/dev/null | grep -qE '^v(1[89]|2[0-9])'; then
  dnf -y module switch-to nodejs:20 || {
    dnf -y module reset nodejs
    dnf -y module enable nodejs:20
    dnf -y distro-sync nodejs npm
  }
fi
node --version
if ! swapon --show | grep -q .; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "=== [2/8] extract code ==="
mkdir -p /opt/btb
tar xzf /root/btb_deploy.tar.gz -C /opt/btb
ls /opt/btb

echo "=== [3/8] backend venv + deps ==="
cd /opt/btb/BTB_AI
python3.11 -m venv .venv
./.venv/bin/pip install --no-cache-dir --upgrade pip -q
./.venv/bin/pip install --no-cache-dir -q torch --index-url https://download.pytorch.org/whl/cpu
./.venv/bin/pip install --no-cache-dir -q -r requirements.txt
./.venv/bin/python -c "import fastapi, langchain, faiss; print('backend deps OK')"

echo "=== [4/8] env config ==="
{ echo; cat /root/btb.env.extra; } >> /opt/btb/BTB_AI/.env
rm -f /root/btb.env.extra

echo "=== [5/8] website build ==="
cd /opt/btb/BTB_Website
npm ci --no-audit --no-fund
npm run build
test -f dist/index.html

echo "=== [6/8] systemd service ==="
cat > /etc/systemd/system/btb-backend.service <<'UNIT'
[Unit]
Description=BTB FastAPI backend (RAG chat + interview admin)
After=network.target

[Service]
WorkingDirectory=/opt/btb/BTB_AI
ExecStart=/opt/btb/BTB_AI/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment=PATH=/opt/btb/BTB_AI/.venv/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now btb-backend

echo "=== [7/8] nginx ==="
cat > /etc/nginx/conf.d/btb.conf <<'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    root /opt/btb/BTB_Website/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 180s;
    }

    # Hashed build assets never change their content — cache them hard.
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location / {
        # HTML must revalidate so deploys show up immediately.
        add_header Cache-Control "no-cache";
        # $uri.html serves the prerendered per-route pages (interviews/<id>.html)
        # directly, with no trailing-slash redirect; /index.html is the SPA fallback.
        try_files $uri $uri.html $uri/ /index.html;
    }
}
NGINX

# Compress text assets on the wire (nginx gzip is built-in). Cuts the JS bundle
# from ~124KB to ~49KB and each prerendered page by ~3x.
cat > /etc/nginx/conf.d/gzip.conf <<'GZIP'
gzip on;
gzip_vary on;
gzip_comp_level 5;
gzip_min_length 256;
gzip_proxied any;
gzip_types text/plain text/css application/javascript application/json image/svg+xml application/xml application/rss+xml application/manifest+json;
GZIP
# The stock nginx.conf ships its own default_server on :80 — disable it.
if grep -q 'listen\s*80 default_server' /etc/nginx/nginx.conf; then
  sed -i 's/listen\s*80 default_server;/listen 8081;/' /etc/nginx/nginx.conf
  sed -i 's/listen\s*\[::\]:80 default_server;/listen [::]:8081;/' /etc/nginx/nginx.conf
fi
nginx -t
systemctl enable --now nginx
systemctl reload nginx

# NOTE: after issuing certs with
#   certbot --nginx -d thebtbpodcast.com -d www.thebtbpodcast.com
# certbot rewrites the block above for :443 serving BOTH names. For SEO, pick one
# canonical host (the apex): drop www from the main block's server_name and add a
# dedicated :443 block that redirects www -> apex. The live server has this:
#   server {
#       listen 443 ssl;
#       server_name www.thebtbpodcast.com;
#       ssl_certificate     /etc/letsencrypt/live/thebtbpodcast.com/fullchain.pem;
#       ssl_certificate_key /etc/letsencrypt/live/thebtbpodcast.com/privkey.pem;
#       include /etc/letsencrypt/options-ssl-nginx.conf;
#       ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
#       return 301 https://thebtbpodcast.com$request_uri;
#   }

echo "=== [8/8] firewall + backend warmup ==="
if systemctl is-active --quiet firewalld; then
  firewall-cmd --permanent --add-service=http
  firewall-cmd --reload
fi
for i in $(seq 1 30); do
  curl -sf -m 3 http://127.0.0.1:8000/health && break
  sleep 2
done
# Warm the RAG stack (embedding model download + FAISS load) so the first
# visitor doesn't wait through it.
curl -sf -m 300 -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"question": "What does Xavier do?"}' | head -c 200 || echo "warmup chat failed (check later)"
echo
echo DEPLOY_OK
