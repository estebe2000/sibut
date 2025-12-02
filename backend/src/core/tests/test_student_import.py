from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import User, StudentProfile, Cohort

class StudentImportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.cohort = Cohort.objects.create(name="TC 2025")

    def test_import_students_csv(self):
        csv_content = (
            "First name,Surname,Email address,ID number\n"
            "John,Doe,john.doe@test.com,123456\n"
            "Jane,Smith,jane.smith@test.com,789012\n"
        ).encode('utf-8-sig')

        file = SimpleUploadedFile("participants.csv", csv_content, content_type="text/csv")

        data = {
            'file': file,
            'cohort_id': self.cohort.id,
            'current_level': 'BUT1',
            'cohort_year': 2025
        }

        response = self.client.post("/api/import/moodle/students", data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(role=User.Role.STUDENT).count(), 2)
        self.assertEqual(StudentProfile.objects.count(), 2)

        u1 = User.objects.get(email="john.doe@test.com")
        self.assertEqual(u1.first_name, "John")
        self.assertEqual(u1.student_profile.student_number, "123456")
        self.assertEqual(u1.student_profile.cohort, self.cohort)

    def test_import_duplicates(self):
        # Create user beforehand
        u = User.objects.create_user(username="existing", email="existing@test.com", first_name="Old", role=User.Role.STUDENT)

        csv_content = (
            "First name,Surname,Email address,ID number\n"
            "New,Name,existing@test.com,99999\n"
        ).encode('utf-8-sig')

        file = SimpleUploadedFile("participants.csv", csv_content, content_type="text/csv")

        data = {
            'file': file,
            'cohort_id': self.cohort.id,
            'current_level': 'BUT1',
            'cohort_year': 2025
        }

        response = self.client.post("/api/import/moodle/students", data)
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        self.assertEqual(json_resp['updated'], 1)

        u.refresh_from_db()
        self.assertEqual(u.first_name, "New")
        # Check profile created/updated
        self.assertTrue(hasattr(u, 'student_profile'))
        self.assertEqual(u.student_profile.student_number, "99999")
