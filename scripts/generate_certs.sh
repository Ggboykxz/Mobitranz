#!/bin/bash
# Genere les certificats SSL auto-signes pour le developpement
# Remplacer par des vrais certificats pour la production

SSL_DIR="$(dirname "$0")/../ssl"
mkdir -p "$SSL_DIR"

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout "$SSL_DIR/key.pem" \
  -out "$SSL_DIR/cert.pem" \
  -subj '/CN=mobitranz.ga/O=MobiTranz/C=GA' \
  -addext "subjectAltName=DNS:mobitranz.ga,DNS:api.mobitranz.ga,DNS:admin.mobitranz.ga"

chmod 644 "$SSL_DIR/cert.pem" "$SSL_DIR/key.pem"
echo "SSL certificates generated in $SSL_DIR"
