from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# A. Core (Utilisateurs & Cursus)

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Étudiant'
        TEACHER = 'TEACHER', 'Enseignant'
        ADMIN = 'ADMIN', 'Administrateur'
        STUDY_DIR = 'STUDY_DIR', 'Directeur des Études'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)

    # first_name, last_name, email are already in AbstractUser

class Cohort(models.Model):
    name = models.CharField(max_length=100) # ex: "TC 2025-2026"
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_number = models.CharField(max_length=50, unique=True) # INE
    cohort_year = models.IntegerField() # ex: 2025
    current_level = models.CharField(max_length=10) # BUT1, BUT2, BUT3
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return f"{self.user.username} - {self.student_number}"


# B. Référentiel Pédagogique (Immuable)

class Competency(models.Model):
    name = models.CharField(max_length=255)
    short_code = models.CharField(max_length=10) # C1, C2
    color_hex = models.CharField(max_length=7) # #RRGGBB
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.short_code} - {self.name}"

class CriticalLearning(models.Model):
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name='critical_learnings')
    code = models.CharField(max_length=20) # AC1.1
    description = models.TextField()
    level = models.IntegerField() # 1, 2, 3

    def __str__(self):
        return f"{self.code} | {self.description}"

# C. Activités & Évaluations (Transactionnel)

class Activity(models.Model):
    class Type(models.TextChoices):
        SAE = 'SAE', 'SAÉ'
        STAGE = 'STAGE', 'Stage'
        PORTFOLIO = 'PORTFOLIO', 'Portfolio'
        PROJET = 'PROJET', 'Projet'

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=Type.choices)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_activities')
    deadline = models.DateTimeField(null=True, blank=True)

    # ActivityTarget: M2M
    critical_learnings = models.ManyToManyField(CriticalLearning, related_name='activities', blank=True)

    def __str__(self):
        return self.title

class EvaluationToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluation_tokens')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='tokens')
    expiration_date = models.DateTimeField()

class Assessment(models.Model):
    class Value(models.TextChoices):
        NOT_ACQUIRED = 'NOT_ACQUIRED', 'Non acquis'
        IN_PROGRESS = 'IN_PROGRESS', 'En cours d\'acquisition'
        ACQUIRED = 'ACQUIRED', 'Acquis'
        MASTERED = 'MASTERED', 'Maîtrisé'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='assessments')
    critical_learning = models.ForeignKey(CriticalLearning, on_delete=models.CASCADE, related_name='assessments')
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='given_assessments')
    value = models.CharField(max_length=20, choices=Value.choices)
    comment = models.TextField(blank=True)
    is_self_assessment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.critical_learning.code} - {self.value}"
