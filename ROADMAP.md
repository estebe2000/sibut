# Roadmap & Idées d'Amélioration - SIBUT

Ce fichier recense les fonctionnalités prévues et les idées pour les futures versions.

## Version 0.002 (Prochaine étape)

### Authentification & Rôles
- [ ] Intégration LDAP complète pour Étudiants et Enseignants.
- [ ] Gestion fine des permissions (Qui peut évaluer qui ?).
- [ ] Interface de connexion spécifique Tuteurs (Token URL).

### Frontend - Student Dashboard
- [ ] Intégration de la librairie de graphiques (Chart.js ou ECharts) pour le Radar des compétences.
- [ ] Liste déroulante des AC avec état de validation (code couleur).
- [ ] Upload de preuves pour le Portfolio (PDF, Images).

### Frontend - Teacher Board
- [ ] Tableau croisé dynamique (Étudiants x Compétences).
- [ ] Fonction "Saisie en masse" pour noter rapidement une activité.
- [ ] **Interface de Validation** : Vue spécifique pour l'entretien (Affichage de l'auto-positionnement étudiant + Champ de validation final).

### UX / UI - Workflow d'Évaluation
- [ ] **Formulaire Étudiant** : Switch "Concernés" (Oui/Non) -> Si Oui, Sélecteur de Fréquence (Rarement, Souvent, Systématiquement).
- [ ] **Visibilité des statuts** : Afficher clairement "En attente entretien" ou "Validé" sur le dashboard.

## Idées Futures (Backlog)

### Pédagogie & APC
- [ ] **Trajectoires d'apprentissage** : Visualiser la progression attendue vs réelle.
- [ ] **Feedback Audio** : Permettre aux enseignants de laisser un commentaire vocal.
- [ ] **Lien SAÉ <-> Compétence** : Assistant IA pour suggérer les AC à évaluer en fonction de la description d'une SAÉ.

### Interopérabilité
- [ ] **LTI (Learning Tools Interoperability)** : Intégration native dans Moodle (pas juste export CSV).
- [ ] **API Publique** : Pour connecter d'autres outils de l'université.

### UX / UI
- [ ] **Mode Sombre (Dark Mode)** : Natif avec DaisyUI.
- [ ] **Mobile App** : PWA optimisée pour l'évaluation sur le terrain (stages).
- [ ] **Notifications** : Emails ou Push pour rappeler les deadlines d'évaluation.

### Technique
- [ ] **Cache Redis** : Pour optimiser les calculs de progression (Dashboard).
- [ ] **Archivage** : Gestion des cohortes passées (Cold storage).
