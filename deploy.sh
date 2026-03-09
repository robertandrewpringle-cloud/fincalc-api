#!/bin/bash
# deploy.sh — Run on Hetzner VPS to deploy/update FinCalc API
# Usage: ./deploy.sh
set -e

DOMAIN="${DOMAIN:-fincalcapi.com}"
EMAIL="${EMAIL:-admin@fincalcapi.com}"

echo "==> Installing dependencies..."
apt-get update -qq
apt-get install -y -qq certbot python3-certbot-nginx git

echo "==> Pulling latest code..."
if [ -d "/opt/fincalcapi" ]; then
    cd /opt/fincalcapi && git pull
else
    git clone https://github.com/robertandrewpringle-cloud/fincalc-api /opt/fincalcapi
    cd /opt/fincalcapi
fi

echo "==> Obtaining SSL certificate..."
certbot certonly --webroot --webroot-path=/var/www/certbot \
    --non-interactive --agree-tos \
    -m "$EMAIL" -d "$DOMAIN" || echo "Cert already exists or renewal skipped."

echo "==> Building and starting containers..."
docker compose build --no-cache
docker compose up -d

echo "==> Verifying deployment..."
sleep 3
curl -sf http://localhost/health && echo "Deployment successful!" || echo "WARNING: health check failed"
