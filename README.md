# SIBUT - Système de Suivi des Compétences (BUT TC)

**Version :** 0.001
**Statut :** Développement Initial

SIBUT est une plateforme web conçue pour gérer le suivi de l'acquisition des compétences (APC) pour le Bachelor Universitaire de Technologie (BUT) Techniques de Commercialisation. Elle permet aux étudiants, enseignants et tuteurs de suivre la progression pédagogique via des tableaux de bord interactifs.

## Fonctionnalités Principales (v0.001)

*   **Architecture Conteneurisée** : Déploiement facile via Docker (Django + Vue + Postgres).
*   **Modèle de Données APC** : Gestion des Compétences, Apprentissages Critiques (AC), et Niveaux.
*   **Import Automatique** : Extraction des compétences depuis le programme officiel (PDF).
*   **API REST** : Backend Django Ninja performant.
*   **Export Moodle** : Génération de CSV pour l'intégration des notes.

## Documentation

*   [Guide Utilisateur](docs/USER_GUIDE.md) : Pour comprendre comment utiliser la plateforme.
*   [Guide de Développement](docs/DEV_GUIDE.md) : Pour installer, tester et contribuer au code.
*   [Roadmap](ROADMAP.md) : Futures fonctionnalités et idées.

## Démarrage Rapide

1.  Assurez-vous d'avoir Docker et Docker Compose installés.
2.  Clonez ce dépôt.
3.  Configurez l'environnement :
    ```bash
    cp .env.example .env
    ```
4.  Lancez la stack :
    ```bash
    docker-compose up --build
    ```
5.  Accédez à l'application sur `http://localhost`.

## Structure du Projet

*   `backend/` : API Django.
*   `frontend/` : Application Vue.js.
*   `reference_docs/` : Documents sources (Programmes PDF, CR réunions).
*   `docs/` : Documentation du projet.

## Auteurs
Projet initié pour le département TC.
