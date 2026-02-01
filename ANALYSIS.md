# Document d'Analyse - COMS.A.S

## 1. Contexte et Objectifs
Le projet vise à fournir une plateforme web moderne et centralisée pour l'association COMS.A.S (anciennement A²ELBM2). L'objectif est de faciliter la gestion des membres, la communication interne/externe, et l'organisation des activités (parrainage, votes, projets).

## 2. Acteurs du Système
*   **Visiteur** : Peut consulter les pages publiques (Accueil, À propos, Actualités, Projets, Galerie).
*   **Membre (Inscrit)** : Peut compléter son profil, s'inscrire aux événements, participer aux votes.
*   **Administrateur** : Gère l'ensemble de la plateforme (validation membres, création contenus, exports).

## 3. Diagramme de Cas d'Utilisation

```mermaid
usecaseDiagram
    actor "Visiteur" as V
    actor "Membre" as M
    actor "Administrateur" as A

    package "COMS.A.S Website" {
        usecase "Consulter Actualités/Projets" as UC1
        usecase "S'inscrire (Devenir Membre)" as UC2
        usecase "Se Connecter" as UC3
        usecase "Gérer Profil" as UC4
        usecase "S'inscrire à un Événement" as UC5
        usecase "Voter (Élection/Concours)" as UC6
        usecase "Valider Membres" as UC7
        usecase "Gérer Contenus (News, Events)" as UC8
        usecase "Gérer Parrainage" as UC9
    }

    V --> UC1
    V --> UC2
    V --> UC3

    M --> UC1
    M --> UC3
    M --> UC4
    M --> UC5
    M --> UC6

    A --> UC1
    A --> UC3
    A --> UC4
    A --> UC7
    A --> UC8
    A --> UC9
```

## 4. Besoins Fonctionnels

### 3.1. Gestion des Membres
*   **Inscription** : Formulaire détaillé (infos personnelles, académiques, professionnelles).
*   **Validation** : Processus de validation par l'admin (statut "actif").
*   **Carte de Membre** : Génération automatique d'une carte PDF avec photo signature et QR Code.
*   **Profil Public** : Annuaire des membres consultable.

### 3.2. Parrainage (Mentorship)
*   **Inscription** : Sessions de parrainage ouvertes par l'admin.
*   **Rôles** : Inscription en tant que Mentor ou Filleul (Mentee) avec choix de domaines.
*   **Matching** : Algorithme ou action manuelle de l'admin pour créer les binômes.
*   **Suivi** : Liste des binômes formés visible publiquement.

### 3.3. Système de Vote (Élections/Concours)
*   **Candidature** : Présentation des candidats (bio, programme).
*   **Vote Sécurisé** : Un vote par membre, vérification par matricule et email.
*   **Résultats** : Affichage graphique des résultats en temps réel ou différé.

### 3.4. Communication et Contenus
*   **Actualités** : Blog avec éditeur riche.
*   **Événements** : Calendrier, compte à rebours, inscription en ligne.
*   **Projets** : Présentation des projets, barre de progression du budget, appels à dons.
*   **Galerie** : Albums photos des événements passés.

### 3.5. Administration (Dashboard)
*   Statistiques globales (KPIs).
*   Gestion CRUD de toutes les entités.
*   Exports Excel/CSV des données.

## 4. Besoins Non-Fonctionnels
*   **Design** : "Premium", moderne, responsive (Mobile First).
*   **Performance** : Chargement rapide, optimisation des images.
*   **Sécurité** : Protection des données personnelles (GDPR compliance basics).
*   **Maintenabilité** : Code clair, modulaire et documenté.
