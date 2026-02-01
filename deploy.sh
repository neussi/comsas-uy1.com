#!/bin/bash
set -e

echo "🚀 Déploiement de a2elbm2.com sur le port 8336..."

# Vérifier que le port 8336 est libre
if sudo lsof -i :8336 | grep -v docker > /dev/null; then
    echo "⚠️  Le port 8336 semble occupé (hors Docker)"
    sudo lsof -i :8336
fi

# Arrêt des conteneurs
docker-compose down

# Mise à jour du code
git pull origin main

# Reconstruction et redémarrage
docker-compose build
docker-compose up -d

# Attendre que le conteneur soit prêt
echo "⏳ Attente du démarrage du conteneur..."
sleep 15

# Migrations
echo "📊 Application des migrations..."
docker-compose exec -T web python manage.py migrate

# Collecte des fichiers statiques (OBLIGATOIRE pour la production)
echo "📁 Collecte des fichiers statiques..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Créer les répertoires média si nécessaire
echo "📁 Configuration des médias..."
docker-compose exec -T web mkdir -p /app/media
docker-compose exec -T web chmod 755 /app/media

# Test de santé
echo "🔍 Test de l'application..."
sleep 5

if curl -f http://localhost:8336 > /dev/null 2>&1; then
    echo "✅ Application en ligne sur le port 8336"
    echo "🌐 Accessible via: http://a2elbm2.com"
    
else
    echo "❌ Problème détecté"
    echo "📋 Logs du conteneur:"
    docker-compose logs --tail=30 web
fi

echo "📊 Status des conteneurs:"
docker-compose ps

echo "📊 Espace disque utilisé:"
docker-compose exec -T web du -sh /app/staticfiles /app/media 2>/dev/null || echo "Répertoires en cours de création"

echo "✅ Déploiement terminé!"

# Afficher les derniers logs
echo "📋 Derniers logs (si problème):"
docker-compose logs --tail=10 web