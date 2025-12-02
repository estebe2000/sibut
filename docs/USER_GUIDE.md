# Guide Utilisateur - SIBUT v0.001

Bienvenue sur SIBUT, la plateforme de suivi des compétences pour le BUT Techniques de Commercialisation.

## Accès à la plateforme

L'application est accessible via votre navigateur web.
- **Frontend (Application)** : `http://localhost` (ou l'URL de production)
- **Backend (API)** : `http://localhost/api`
- **Administration** : `http://localhost/admin`

## Rôles Utilisateurs

### 1. Étudiant
* **Tableau de Bord 360** : Visualisez votre progression par compétence via un graphique radar.
* **Suivi des AC** : Consultez le statut de validation de vos Apprentissages Critiques (AC).
* **Auto-évaluation** : (À venir) Possibilité de s'auto-évaluer sur certaines activités.

### 2. Enseignant
* **Teacher Board** : Vue d'ensemble de la classe.
* **Évaluation** : Notez les étudiants sur les AC spécifiques liés à vos activités (SAÉ, Stages, Projets).
* **Création d'Activités** : Définissez des activités pédagogiques et liez-les aux AC du référentiel.

### 3. Tuteur Entreprise
* **Accès Simplifié** : Recevez un lien magique par email pour évaluer votre stagiaire sans avoir besoin de créer un compte.

### 4. Administrateur
* **Gestion des Utilisateurs** : Création des comptes (ou import LDAP), gestion des cohortes.
* **Import Référentiel** : Importation automatique des compétences depuis le programme officiel (PDF).
* **Export Moodle** : Exportation des résultats au format CSV compatible Moodle.

## Fonctionnalités Clés

### Importation des Données

#### 1. Référentiel de Compétences
Le système supporte deux modes :
* **Automatique (PDF)** : Via la commande d'administration, pour le programme national BUT TC.
* **Moodle (CSV)** : Via l'API, pour importer un référentiel existant dans Moodle.
   * Format attendu : CSV Moodle Competency framework.
   * Colonnes : `ID number`, `Short name`, `Description`, `Parent ID number`.

#### 2. Importation des Étudiants (Moodle)
Il est possible d'importer la liste des étudiants depuis un export CSV "Participants" de Moodle.
* **Endpoint** : `POST /api/import/moodle/students`
* **Format CSV** : Colonnes `First name`, `Surname`, `Email address`, `ID number` (INE).
* **Données requises lors de l'import** :
    * Fichier CSV
    * ID de la Cohorte (Promo)
    * Niveau actuel (ex: BUT1)
    * Année de la cohorte (ex: 2025)

### Évaluation par Compétences (APC)
Le processus d'évaluation se déroule en deux temps :

1. **Auto-positionnement (Étudiant/Tuteur)** :
   - L'étudiant déclare s'il est concerné par la compétence ("Oui/Non").
   - Si oui, il indique la **fréquence** de mobilisation : "Rarement", "Souvent" ou "Systématiquement".
   *Ce positionnement est déclaratif et n'a pas valeur de validation.*

2. **Validation (Enseignant)** :
   - L'acquisition réelle n'est validée qu'après la remise d'un écrit réflexif et un entretien oral.
   - L'enseignant attribue alors le niveau final :
     - **Non acquis**
     - **En cours d'acquisition**
     - **Acquis**
     - **Maîtrisé**

### Export Moodle
Les administrateurs peuvent télécharger un fichier CSV contenant les évaluations pour les réimporter dans le carnet de notes Moodle.
