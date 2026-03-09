#!/bin/bash
# deploy.sh — Run on Hetzner VPS to deploy/update FinCalc API
# Usage: ./deploy.sh
set -e

DOMAIN="${DOMAIN:-fincalcapi.com}"
EMAIL="${EMAIL:-admin@fincalcapi.com}"

echo "==> Installing dependencies..."
apt-get update -qq
apt-get install -y -qq docker.io docker-compose-plugin certbot python3-certbot-nginx git

echo "==> Pulling latest code..."
if [ -d "/opt/fincalcapi" ]; then
    cd /opt/fincalcapi && git pull
else
    git clone https://github.com/YOUR_GITHUB_USERNAME/fincalc-api /opt/fincalcapi
    cd /opt/fincalcapi
fi

echo "==> Obtaining SSL certificate..."
certbot certonly --standalone --non-interactive --agree-tos \
    -m "$EMAIL" -d "$DOMAIN" --pre-hook "docker compose down" \
    --post-hook "docker compose up -d" 2>/dev/null || echo "Cert already exists, skipping."

echo "==> Building and starting containers..."
docker compose build --no-cache
docker compose up -d

echo "==> Verifying deployment..."
sleep 3
curl -sf http://localhost/health && echo "Deployment successful!" || echo "WARNING: health check failed"
