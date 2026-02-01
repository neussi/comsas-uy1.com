# COMS.A.S Website

Plateforme web officielle de **Computer Science Association (COMS.A.S)** de l'Université de Yaoundé 1 (anciennement A²ELBM2).

Elle permet la gestion des membres, des événements, des projets, ainsi que l'organisation des parrainages et des votes en ligne.

## Fonctionnalités Principales

*   **Gestion des Membres** : Inscription, annuaire, profils publics et cartes de membre (PDF + QR Code).
*   **Parrainage (Mentorship)** : Inscription Mentor/Mentee, algorithme de matching structuré.
*   **Événements & Actualités** : Agenda, inscriptions aux événements, blog d'actualités.
*   **Projets** : Suivi des projets de l'association, appels à contribution.
*   **Vote Sécurisé** : Système d'élection avec vérification par matricule/email et statistiques en temps réel.
*   **Administration** : Dashboard complet avec graphiques et statistiques (Chart.js).

## Installation

1.  **Cloner le projet** :
    ```bash
    git clone https://github.com/votre-compte/comsas-website.git
    cd comsas-website
    ```

2.  **Créer un environnement virtuel** :
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Sur Linux/Mac
    # venv\Scripts\activate  # Sur Windows
    ```

3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
    *(Si `requirements.txt` n'existe pas encore, installez les paquets manuellement : `django ckeditor pillow qrcode reportlab`)*

4.  **Appliquer les migrations** :
    ```bash
    python manage.py migrate
    ```

5.  **Créer un superutilisateur** :
    ```bash
    python manage.py createsuperuser
    ```

6.  **Lancer le serveur** :
    ```bash
    python manage.py runserver
    ```

## Technologies

*   **Backend** : Django 4.2 (Python)
*   **Frontend** : Bootstrap 5, Chart.js, HTML5/CSS3
*   **Base de données** : SQLite (Dev), PostgreSQL (Prod recommandé)

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.