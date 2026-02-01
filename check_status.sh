#!/bin/bash

echo "🔍 Vérification de l'état de a2elnm2.com..."

# Status Docker
echo "📦 Status Docker:"
docker-compose ps

# Port 8436
echo "🔌 Port 8336:"
if sudo lsof -i :8336 > /dev/null; then
    sudo lsof -i :8336
else
    echo "❌ Rien n'écoute sur le port 8436"
fi

# Test application
echo "🌐 Test application:"
curl -I http://localhost:8336 2>/dev/null || echo "❌ Application non accessible"

# Test domaine
echo "🌍 Test domaine:"
curl -I http://a2elnm2.com 2>/dev/null || echo "❌ Domaine non accessible"

# Logs récents
echo "📋 Derniers logs:"
docker-compose logs --tail=5 web
