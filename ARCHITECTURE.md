# Architecture du Système COMS.A.S

## Vue d'Ensemble
L'architecture de la plateforme COMS.A.S est basée sur une architecture monolithique modulaire utilisant le framework Django (MVT - Model View Template). Elle est conçue pour être évolutive, sécurisée et facile à maintenir.

## Diagramme de Composants

```mermaid
graph TD
    User[Utilisateur] -->|HTTP/HTTPS| WebServer[Serveur Web (Nginx/Apache)]
    WebServer -->|WSGI/Gunicorn| DjangoApp[Application Django]
    
    subgraph "Application Django (Backend)"
        Auth[Authentification & Permissions]
        MainApp[App 'main' (Front Office)]
        AdminDashboard[App 'admin_dashboard' (Back Office)]
        
        MainApp --> Models
        AdminDashboard --> Models
    end
    
    DjangoApp --> DB[(Base de Données PostgreSQL)]
    DjangoApp --> Static[Fichiers Statiques & Media]
    DjangoApp --> EmailService[Service SMTP]
```

## Diagramme de Déploiement

```mermaid
graph LR
    Client[Client (Navigateur/Mobile)] -- HTTPS --> Nginx[Serveur Reverse Proxy (Nginx)]
    Nginx -- Proxy --> Gunicorn[Serveur App (Gunicorn)]
    
    subgraph "Serveur Application"
        Gunicorn -- WSGI --> Django[Instance Django]
        Django -- Read/Write --> FS[Système de Fichiers (Static/Media)]
    end
    
    Django -- SQL (5432) --> DB[(PostgreSQL)]
    Django -- SMTP (587) --> Mail[Serveur Email (Google/Outlook)]
```

## Structure des Dossiers

*   **`comsas_website/`** : Cœur du projet (settings, urls, wsgi/asgi).
*   **`main/`** : Application principale gérant le Front Office (pages publiques, profils, événements).
*   **`admin_dashboard/`** : Application dédiée au Back Office (administration personnalisée, chartes, gestion).
*   **`templates/`** : Gabarits HTML (divisés en `main/` et `admin_dashboard/`).
*   **`static/`** : Fichiers CSS, JS, Images statiques.
*   **`media/`** : Fichiers uploadés par les utilisateurs (photos de profil, images de projets).

## Choix Technologiques

### Backend
*   **Django 4.2 LTS** : Framework robuste, "batteries included".
*   **Pillow** : Gestion des images.
*   **ReportLab** : Génération de PDF pour les cartes de membres.
*   **QRCode** : Génération de codes QR pour les profils.

### Frontend
*   **Bootstrap 5** : Système de grille et composants UI responsives.
*   **FontAwesome** : Icônes vectorielles.
*   **Chart.js** : Visualisation de données (statistiques admin).
*   **CKEditor** : Éditeur de texte riche pour les contenus (news, projets).

### Base de Données
*   **SQLite** (Développement) : Simple, fichier unique.
*   **PostgreSQL** (Production) : Recommandé pour la robustesse et la gestion de la concurrence.

## Sécurité
*   Protection CSRF native Django.
*   Authentification forte (User Model étendu).
*   Décorateurs `@login_required` et `@staff_member_required` pour protéger les vues.
*   Validation des uploads (extensions autorisées).
