from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Competency, CriticalLearning
import io

class MoodleImportTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_import_moodle_csv(self):
        csv_content = (
            "Parent ID number,ID number,Short name,Description\n"
            ",C1,Marketing,Competency 1\n"
            "C1,AC11.01,AC11.01,AC Description 1\n"
        ).encode('utf-8-sig')

        file = SimpleUploadedFile("moodle.csv", csv_content, content_type="text/csv")

        response = self.client.post("/api/import/moodle/framework", {'file': file})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Competency.objects.count(), 1)
        self.assertEqual(CriticalLearning.objects.count(), 1)

        c = Competency.objects.first()
        self.assertEqual(c.short_code, "C1")

        ac = CriticalLearning.objects.first()
        self.assertEqual(ac.code, "AC11.01")
        self.assertEqual(ac.competency, c)

    def test_invalid_csv(self):
        file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        response = self.client.post("/api/import/moodle/framework", {'file': file})
        self.assertEqual(response.status_code, 400)
