from django.test import TestCase, Client
from core.models import Competency, CriticalLearning, User, Assessment, Activity
import json

class AssessmentLogicTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.competency = Competency.objects.create(name="Marketing", short_code="C1", color_hex="#ffffff")
        self.ac = CriticalLearning.objects.create(competency=self.competency, code="AC11.01", description="Test AC", level=1)

        self.student = User.objects.create_user(username="student1", password="password", role=User.Role.STUDENT)
        self.teacher = User.objects.create_user(username="teacher1", password="password", role=User.Role.TEACHER)

        self.activity = Activity.objects.create(title="Test Activity", type="SAE")

    def test_student_cannot_set_validation_level(self):
        self.client.force_login(self.student)
        payload = {
            "student_id": self.student.id,
            "critical_learning_id": self.ac.id,
            "activity_id": self.activity.id,
            "is_concerned": True,
            "frequency": "OFTEN",
            "validation_level": "ACQUIRED" # Should be forbidden
        }
        response = self.client.post("/api/assessments", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_student_must_set_frequency_if_concerned(self):
        self.client.force_login(self.student)
        payload = {
            "student_id": self.student.id,
            "critical_learning_id": self.ac.id,
            "activity_id": self.activity.id,
            "is_concerned": True,
            # Missing frequency
        }
        response = self.client.post("/api/assessments", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 422)

    def test_teacher_can_validate(self):
        self.client.force_login(self.teacher)
        payload = {
            "student_id": self.student.id,
            "critical_learning_id": self.ac.id,
            "activity_id": self.activity.id,
            "validation_level": "ACQUIRED"
        }
        response = self.client.post("/api/assessments", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        assessment_id = response.json()['id']
        assessment = Assessment.objects.get(id=assessment_id)
        self.assertEqual(assessment.validation_level, "ACQUIRED")
        self.assertEqual(assessment.validation_status, "VALIDATED")

    def test_validate_endpoint(self):
        # Create a pending assessment
        assessment = Assessment.objects.create(
            student=self.student,
            activity=self.activity,
            critical_learning=self.ac,
            is_concerned=True,
            frequency="OFTEN",
            validation_status="PENDING_WRITING"
        )

        self.client.force_login(self.teacher)
        payload = {
            "validation_status": "VALIDATED",
            "validation_level": "MASTERED"
        }
        response = self.client.put(f"/api/assessments/{assessment.id}/validate", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)

        assessment.refresh_from_db()
        self.assertEqual(assessment.validation_status, "VALIDATED")
        self.assertEqual(assessment.validation_level, "MASTERED")
