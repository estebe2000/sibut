# sibut
gestion competences but 
# PROJET : SYS-COMPETENCES-IUT (BUT TC)
> **Cahier des Charges Technique et Fonctionnel pour Assistant IA**

## 🤖 INSTRUCTIONS CRITIQUES POUR L'IA
Ce document définit la "Vérité Terrain". Tu dois t'y référer avant de générer la moindre ligne de code.
**Objectif :** Créer une plateforme Web & Mobile (PWA) pour le suivi de l'acquisition des compétences (APC) des étudiants en BUT Techniques de Commercialisation (TC).

---

## 1. STACK TECHNIQUE IMPOSÉE (STRICT)
Le projet doit respecter scrupuleusement ces choix technologiques :

* **Backend :** Python **Django 5.x**.
    * *Justification :* Utilisation de l'Admin Panel natif pour la gestion administrative et de l'ORM pour les relations complexes.
    * *API :* **Django Ninja** (ou DRF) pour exposer les données au frontend.
* **Base de Données :** **PostgreSQL** (Obligatoire pour l'intégrité relationnelle et le support JSONB).
* **Frontend :** **Vue.js 3** (Composition API) + **Vite**.
    * *UI Kit :* **Tailwind CSS** + **DaisyUI** (pour un développement rapide et mobile-friendly).
* **Authentification :**
    * Interne : Login/Pass (ou LDAP futur) pour Enseignants/Étudiants/Admin.
    * Externe : **Magic Link** (Token unique via URL) pour les Tuteurs Entreprise (Pas de compte utilisateur complet).

---

## 2. INFRASTRUCTURE & DÉPLOIEMENT (DOCKER)
Le projet doit être entièrement conteneurisé pour un déploiement "clé en main". **Aucune dépendance externe (SaaS) pour la BDD.**

**Structure `docker-compose.yml` attendue :**

### A. Service Database (`db`)
* **Image :** `postgres:15-alpine`.
* **Persistance :** Utilisation **OBLIGATOIRE** d'un `volume` Docker nommé (ex: `postgres_data`) pour la persistance des données entre les redémarrages.
* **Config :** Variables d'environnement lues depuis un fichier `.env`.

### B. Service Backend (`api`)
* **Build :** `Dockerfile` basé sur Python 3.11-slim.
* **Cycle de vie :** Doit inclure un script "wait-for-it" pour attendre que le service `db` soit prêt avant de lancer les migrations (`python manage.py migrate`) puis le serveur (`gunicorn`/`uvicorn`).
* **Volumes :** Montage nécessaire pour les fichiers `media` (Preuves du portfolio uploadées par les élèves).

### C. Service Frontend (`web`)
* **Build :** Multi-stage build (Node.js pour builder -> Nginx pour servir).
* **Reverse Proxy :** Configuration Nginx pour servir l'app Vue.js et rediriger les requêtes `/api` vers le conteneur Backend.

---

## 3. ANALYSE DES ENTRÉES (Dossier `/reference_docs`)
L'application sera alimentée par les fichiers `.docx` présents dans le dossier `/reference_docs`.
**Structure des données à extraire (Parsing) :**
1.  **Niveau (Level) :** BUT1, BUT2, BUT3.
2.  **Compétence (Competency) :** Titre, Description, Couleur.
3.  **Apprentissage Critique (CriticalLearning - AC) :** Le critère atomique d'évaluation (ex: "AC11.01 | Analyser l'environnement").
4.  **Ressource/SAÉ :** Lien théorique entre un module pédagogique et des AC.

---

## 4. MODÈLE DE DONNÉES CIBLE (SCHEMA DB)

L'IA doit implémenter ce schéma relationnel (MCD) :

### A. Core (Utilisateurs & Cursus)
* **User :** `id`, `email`, `role` (STUDENT, TEACHER, ADMIN, STUDY_DIR), `first_name`, `last_name`.
* **StudentProfile :** `user_id`, `student_number` (INE), `cohort_year` (ex: 2025), `current_level` (BUT1).
* **Cohort (Promo) :** `id`, `name` (ex: "TC 2025-2026"), `is_active`.

### B. Référentiel Pédagogique (Immuable)
* **Competency :** `id`, `name`, `short_code` (C1, C2), `color_hex`.
* **CriticalLearning (AC) :** `id`, `competency_id`, `code` (AC1.1), `description`, `level` (1, 2, 3).
    * *Note : C'est l'unité de base de l'évaluation.*

### C. Activités & Évaluations (Transactionnel)
* **Activity :** `id`, `title`, `type` (SAE, STAGE, PORTFOLIO, PROJET), `description`, `owner_id` (Teacher), `deadline`.
* **ActivityTarget :** Table de liaison `Activity` <-> `CriticalLearning` (Quels AC sont évalués ?).
* **EvaluationToken :** `id`, `token` (UUID), `student_id`, `activity_id`, `expiration_date` (Pour l'accès tuteur externe).
* **Assessment (L'évaluation) :**
    * `id`, `student_id`, `activity_id`
    * `critical_learning_id` (FK vers l'AC spécifique)
    * `evaluator_id` (Peut être null si tuteur externe)
    * `value` (Enum: NOT_ACQUIRED, IN_PROGRESS, ACQUIRED, MASTERED)
    * `comment` (Text)
    * `is_self_assessment` (Boolean).

---

## 5. RÈGLES MÉTIER (BUSINESS LOGIC)

1.  **Logique de Validation :** Pas de moyenne sur 20. Une compétence est validée si les AC associés sont majoritairement "ACQUIS".
2.  **Suivi Longitudinal (3-5 ans) :** Si un étudiant redouble (change de `Cohort`), il conserve ses `Assessment` passés. Le système doit afficher son historique complet.
3.  **Flux Tuteur Entreprise :**
    * L'étudiant déclare son stage.
    * Le système envoie un mail au tuteur avec un lien : `domain.com/eval/uuid-token`.
    * Le tuteur accède à une interface simplifiée (Mobile First) pour évaluer sans login.

---

## 6. INSTRUCTIONS UI (DASHBOARDS)

1.  **Student Dashboard (Vue 360) :**
    * **Spider Chart (Radar) :** 5 axes correspondant aux 5 compétences du BUT TC.
    * Affichage de la progression en temps réel.
2.  **Teacher Board :**
    * Vue tabulaire (Matrice Élèves x AC).
    * Fonctionnalité "Bulk Evaluate" (Noter rapidement).

---

## 7. LIVRABLES ATTENDUS DE L'IA

Tu dois fournir dans l'ordre :
1.  Le fichier **`docker-compose.yml`** complet.
2.  Les fichiers **`Dockerfile`** (Backend et Frontend).
3.  Le script **`models.py`** (Django) respectant scrupuleusement le schéma ci-dessus.
4.  Un fichier **`.env.example`** pour la configuration.
