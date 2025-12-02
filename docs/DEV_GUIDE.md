# Guide de Développement - SIBUT v0.001

Ce document détaille l'architecture technique et les procédures pour les développeurs.

## Architecture

* **Backend** : Django 5.x + Django Ninja (API).
* **Base de Données** : PostgreSQL 15.
* **Frontend** : Vue.js 3 + Vite + Tailwind CSS + DaisyUI.
* **Infrastructure** : Docker Compose (db, api, web).

## Installation & Démarrage

### Pré-requis
* Docker & Docker Compose
* Git

### Lancement Rapide

1.  **Cloner le dépôt**
    ```bash
    git clone <repo_url>
    cd sibut
    ```

2.  **Configuration**
    Copiez le fichier d'exemple `.env` :
    ```bash
    cp .env.example .env
    ```
    *Note : Modifiez les valeurs si nécessaire pour la production.*

3.  **Démarrer les conteneurs**
    ```bash
    docker-compose up --build
    ```
    L'application sera accessible sur `http://localhost`.

## Commandes Utiles (Backend)

Exécuter des commandes dans le conteneur `api` :

```bash
# Entrer dans le shell du conteneur
docker-compose exec api bash

# Lancer les migrations
python src/manage.py migrate

# Créer un superutilisateur
python src/manage.py createsuperuser

# Importer le référentiel depuis le PDF (reference_docs/techniques-de-commercialisation.pdf)
python src/manage.py import_reference_docs
```

## Structure du Code

### Backend (`backend/src/`)
*   `core/` : Application principale contenant les modèles (User, Competency, Assessment).
    *   `models.py` : Définition des données.
      *   `Assessment` contient désormais la logique duale : `frequency` (Déclaratif) vs `validation_level` (Validation enseignante).
    *   `api.py` : Endpoints de l'API REST.
    *   `management/commands/import_reference_docs.py` : Script de parsing PDF.
    *   `utils/moodle_export.py` : Logique d'export CSV.
    *   `utils/moodle_import.py` : Logique d'import CSV Moodle.
    *   `utils/student_import.py` : Logique d'import CSV Étudiants.

## API & Payloads (Logique d'Évaluation)

### Enumérations

**Fréquence (Déclaratif Étudiant/Tuteur)**
*   `RARELY` : Rarement
*   `OFTEN` : Souvent
*   `SYSTEMATICALLY` : Systématiquement

**Niveau de Validation (Enseignant)**
*   `NOT_ACQUIRED` : Non acquis
*   `IN_PROGRESS` : En cours d'acquisition
*   `ACQUIRED` : Acquis
*   `MASTERED` : Maîtrisé

### Exemples de Payloads JSON

**1. Déclaration Étudiant (Auto-positionnement)**
`POST /api/assessments`

```json
{
  "student_id": 1,
  "critical_learning_id": 10,
  "activity_id": 5,
  "is_concerned": true,
  "frequency": "OFTEN",
  "comment": "J'ai mobilisé cette compétence lors de la phase de prospection."
}
```
*Note : `validation_level` doit être omis ou null. Sinon `403 Forbidden`.*

**2. Validation Enseignant**
`POST /api/assessments` (Création directe) ou `PUT /api/assessments/{id}/validate` (Validation d'une déclaration)

```json
{
  "student_id": 1,
  "critical_learning_id": 10,
  "activity_id": 5,
  "validation_level": "ACQUIRED",
  "validation_status": "VALIDATED",
  "comment": "Validé suite à l'entretien du 20/10."
}
```

### Frontend (`frontend/`)
*   `src/` : Code source Vue.js.
*   `Dockerfile` : Build multi-stage (Node -> Nginx).

## TODOs & Dette Technique

### Backend
*   [ ] **Authentification** : Implanter `django-auth-ldap` pour la connexion via l'annuaire de l'IUT.
*   [ ] **Magic Link** : Finaliser l'envoi d'emails pour les tuteurs (SMTP non configuré).
*   [ ] **Tests** : Augmenter la couverture de tests (actuellement tests unitaires basiques).
*   [ ] **Sécurité** : Passer `DEBUG=False` et configurer `ALLOWED_HOSTS` via env.

### Frontend
*   [ ] **Intégration API** : Connecter les composants Vue aux endpoints API (actuellement mock/squelette).
*   [ ] **Vues** : Développer les vues détaillées (Détail étudiant, Grille enseignant).

### DevOps
*   [ ] **CI/CD** : Mettre en place un pipeline pour les tests et le déploiement.
*   [ ] **HTTPS** : Configurer Nginx pour SSL/TLS (Certbot).
