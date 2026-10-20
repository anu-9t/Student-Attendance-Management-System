#!/bin/sh
set -eu

CERT_DIR="/etc/nginx/certs"
CERT_FILE="${TLS_CERT_FILE:-${CERT_DIR}/server.crt}"
KEY_FILE="${TLS_KEY_FILE:-${CERT_DIR}/server.key}"
TLS_DOMAIN="${TLS_DOMAIN:-localhost}"
TLS_DAYS="${TLS_DAYS:-365}"

mkdir -p "$(dirname "$CERT_FILE")" "$(dirname "$KEY_FILE")"

# Generate a development certificate when no certificate has been mounted.
# Production deployments should mount trusted certificate and key files instead.
if [ ! -s "$CERT_FILE" ] || [ ! -s "$KEY_FILE" ]; then
    echo "Generating a self-signed development certificate for ${TLS_DOMAIN}"
    openssl req -x509 -nodes -newkey rsa:2048 \
        -days "$TLS_DAYS" \
        -subj "/CN=${TLS_DOMAIN}" \
        -addext "subjectAltName=DNS:${TLS_DOMAIN}" \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        >/dev/null 2>&1
fi

exec nginx -g 'daemon off;'
