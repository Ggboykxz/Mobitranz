#!/bin/bash
# ============================================================
# MobiTranz - Script de Déploiement Production
# ============================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "  🚀 MobiTranz - Déploiement Production"
echo "========================================"

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Error: .env.production not found!${NC}"
    echo "Copiez .env.production.example vers .env.production et configurez les secrets"
    exit 1
fi

# Generate secrets if needed
generate_secrets() {
    echo -e "${YELLOW}Génération des secrets...${NC}"
    
    # Generate SECRET_KEY and JWT_SECRET
    if grep -q "CHANGE_ME_IN_PRODUCTION" .env.production; then
        SECRET_KEY=$(openssl rand -hex 32)
        JWT_SECRET=$(openssl rand -hex 32)
        AES_KEY=$(openssl rand -hex 32)
        
        sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.production
        sed -i "s/^JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env.production
        sed -i "s/^AES_MASTER_KEY=.*/AES_MASTER_KEY=$AES_KEY/" .env.production
    fi
    
    echo -e "${GREEN}✓ Secrets générés${NC}"
}

# Generate SSL certificates
generate_ssl() {
    echo -e "${YELLOW}Génération des certificats SSL...${NC}"
    
    mkdir -p ssl
    
    if [ ! -f "ssl/cert.pem" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem -out ssl/cert.pem \
            -subj "/C=GA/ST=Estuaire/L=Libreville/O=MobiTranz/CN=*.mobitranz.ga"
        echo -e "${YELLOW}⚠️  Certificat auto-signé créé (à remplacer en prod)${NC}"
    fi
    
    echo -e "${GREEN}✓ SSL configuré${NC}"
}

# Pull latest images
pull_images() {
    echo -e "${YELLOW}Téléchargement des images...${NC}"
    docker-compose -f docker-compose.prod.yml pull
    echo -e "${GREEN}✓ Images téléchargées${NC}"
}

# Build custom images
build_images() {
    echo -e "${YELLOW}Construction des images...${NC}"
    docker-compose -f docker-compose.prod.yml build --no-cache
    echo -e "${GREEN}✓ Images construites${NC}"
}

# Run database migrations
run_migrations() {
    echo -e "${YELLOW}Exécution des migrations...${NC}"
    docker-compose -f docker-compose.prod.yml exec -T backend python -m alembic upgrade head
    echo -e "${GREEN}✓ Migrations terminées${NC}"
}

# Deploy services
deploy() {
    echo -e "${YELLOW}Déploiement des services...${NC}"
    
    # Stop old containers
    docker-compose -f docker-compose.prod.yml down
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services
    sleep 10
    
    # Check health
    check_health
}

# Check services health
check_health() {
    echo -e "${YELLOW}Vérification de la santé des services...${NC}"
    
    services=("backend" "db" "redis" "nginx")
    
    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.prod.yml ps | grep -q "${service}.*Up"; then
            echo -e "${GREEN}✓ $service${NC}"
        else
            echo -e "${RED}✗ $service${NC}"
        fi
    done
}

# Show logs
logs() {
    docker-compose -f docker-compose.prod.yml logs -f --tail=100
}

# Show status
status() {
    docker-compose -f docker-compose.prod.yml ps
}

# Menu
case "${1:-deploy}" in
    generate-secrets)
        generate_secrets
        ;;
    generate-ssl)
        generate_ssl
        ;;
    build)
        build_images
        ;;
    migrate)
        run_migrations
        ;;
    deploy)
        generate_secrets
        generate_ssl
        pull_images
        deploy
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    health)
        check_health
        ;;
    *)
        echo "Usage: $0 {deploy|build|logs|status|health|generate-secrets|generate-ssl}"
        exit 1
        ;;
esac

echo -e "${GREEN}========================================"
echo "  ✅ Déploiement terminé!"
echo "========================================"