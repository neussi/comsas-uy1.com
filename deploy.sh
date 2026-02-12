#!/bin/bash
set -e

echo " Déploiement de comsas-uy1.com sur le port 35467..."

# Vérifier que le port 35467 est libre
if sudo lsof -i :35467 | grep -v docker > /dev/null; then
    echo "  Le port 35467 semble occupé (hors Docker)"
    sudo lsof -i :35467
fi

# Arrêt des conteneurs
docker-compose down

# Mise à jour du code
git pull origin main

# Reconstruction et redémarrage
docker-compose build
docker-compose up -d

# Attendre que le conteneur soit prêt
echo " Attente du démarrage du conteneur..."
sleep 20

# Migrations
echo " Application des migrations..."
docker-compose exec -T web python manage.py migrate

# Collecte des fichiers statiques (OBLIGATOIRE pour la production)
echo " Collecte des fichiers statiques..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Créer les répertoires média si nécessaire
echo " Configuration des médias..."
docker-compose exec -T web mkdir -p /app/media
docker-compose exec -T web chmod 755 /app/media

# Test de santé
echo " Test de l'application..."
sleep 5

if curl -f http://localhost:35467 > /dev/null 2>&1; then
    echo " Application en ligne sur le port 35467"
    echo " Accessible via: https://comsas-uy1.com"
    
else
    echo " Problème détecté"
    echo " Logs du conteneur:"
    docker-compose logs --tail=30 web
fi

echo " status des conteneurs:"
docker-compose ps

echo " Espace disque utilisé:"
docker-compose exec -T web du -sh /app/staticfiles /app/media 2>/dev/null || echo "Répertoires en cours de création"

echo "✅ Déploiement terminé!"

# =============================================================================
# CONFIGURATION APACHE (AUTOMATISÉE)
# =============================================================================

echo "🔧 Configuration d'Apache..."

APACHE_CONF="/etc/apache2/sites-available/comsas-uy1.conf"

# Création du fichier de configuration
sudo bash -c "cat > $APACHE_CONF" <<EOF
<VirtualHost *:80>
    ServerName comsas-uy1.com
    ServerAlias www.comsas-uy1.com

    # Préservation du host original
    ProxyPreserveHost On

    # Redirection du trafic vers ton backend local sur le port 35467
    ProxyPass / http://localhost:35467/
    ProxyPassReverse / http://localhost:35467/

    # En-têtes utiles pour Django
    RequestHeader set X-Forwarded-For expr=%{REMOTE_ADDR}
    RequestHeader set X-Forwarded-Proto expr=%{REQUEST_SCHEME}

    # Gestion des fichiers statiques et médias
    Alias /static /home/npe-tech/Projets/Comsas/staticfiles
    Alias /media  /home/npe-tech/Projets/Comsas/media

    <Directory "/home/npe-tech/Projets/Comsas/staticfiles">
        Require all granted
    </Directory>

    <Directory "/home/npe-tech/Projets/Comsas/media">
        Require all granted
    </Directory>

    # Logs du site
    ErrorLog \${APACHE_LOG_DIR}/comsas-uy1_error.log
    CustomLog \${APACHE_LOG_DIR}/comsas-uy1_access.log combined

    # Redirection vers HTTPS (si certbot est configuré, sinon commenter cette section)
    # RewriteEngine On
    # RewriteCond %{SERVER_NAME} =comsas-uy1.com [OR]
    # RewriteCond %{SERVER_NAME} =www.comsas-uy1.com
    # RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>
EOF

echo " Fichier de configuration créé : $APACHE_CONF"

# Activation du site et redémarrage d'Apache
echo "Activation du site..."
sudo a2ensite comsas-uy1.conf
sudo systemctl reload apache2

echo " Configuration Apache appliquée !"

# Afficher les derniers logs
echo " Derniers logs (si problème):"
docker-compose logs --tail=10 web