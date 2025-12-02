from django.test import TestCase
from core.models import Competency, CriticalLearning, User, StudentProfile, Cohort, Assessment, Activity

class CoreModelTest(TestCase):
    def setUp(self):
        self.competency = Competency.objects.create(name="Marketing", short_code="C1", color_hex="#ffffff")
        self.ac = CriticalLearning.objects.create(competency=self.competency, code="AC11.01", description="Test AC", level=1)
        self.user = User.objects.create_user(username="student1", password="password")
        self.cohort = Cohort.objects.create(name="TC 2025")
        self.profile = StudentProfile.objects.create(user=self.user, student_number="12345", cohort_year=2025, current_level="BUT1", cohort=self.cohort)
        self.activity = Activity.objects.create(title="Test Activity", type="SAE")

    def test_assessment_creation(self):
        assessment = Assessment.objects.create(
            student=self.user,
            activity=self.activity,
            critical_learning=self.ac,
            validation_level="ACQUIRED",
            role_evaluator="TEACHER"
        )
        self.assertEqual(Assessment.objects.count(), 1)
        self.assertEqual(assessment.validation_level, "ACQUIRED")

    def test_competency_ac_relation(self):
        self.assertEqual(self.competency.critical_learnings.count(), 1)
        self.assertEqual(self.competency.critical_learnings.first().code, "AC11.01")
