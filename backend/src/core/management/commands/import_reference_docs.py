import os
from django.core.management.base import BaseCommand
from core.models import Competency, CriticalLearning
import pypdf
import re

class Command(BaseCommand):
    help = 'Import Competencies and Critical Learnings from reference_docs'

    def handle(self, *args, **options):
        self.stdout.write("Starting import...")
        base_dir = '/app'
        ref_dir = os.path.join(base_dir, 'reference_docs')
        if not os.path.exists(ref_dir):
            ref_dir = os.path.join(os.getcwd(), 'reference_docs')

        pdf_path = os.path.join(ref_dir, 'techniques-de-commercialisation.pdf')
        if os.path.exists(pdf_path):
            self.parse_pdf(pdf_path)
        else:
            self.stderr.write(f"PDF not found at {pdf_path}")

    def parse_pdf(self, path):
        self.stdout.write(f"Parsing {path}...")
        try:
            reader = pypdf.PdfReader(path)

            # Improved regexes
            ac_pattern = re.compile(r'AC(\d+\.\d+([A-Z]+)?)\s*\|\s*([^\n]+)', re.IGNORECASE)
            # Pattern for ACs like AC24.01MMPV where MMPV is the suffix
            # AC\s*(\d+)(\.\d+)([A-Z]+)?\s*\|\s*([^\n]+)

            # Dictionary to store competencies
            competencies = {}

            # Hardcoded list of competencies as fallback/verification
            known_competencies = {
                1: "Marketing",
                2: "Vente",
                3: "Communication commerciale",
                4: "Management",
                5: "Retail marketing"
            }

            # Pre-create known competencies
            for cid, cname in known_competencies.items():
                c, _ = Competency.objects.get_or_create(
                    short_code=f"C{cid}",
                    defaults={
                        'name': cname,
                        'color_hex': self.get_color(cid)
                    }
                )
                competencies[cid] = c

            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                lines = text.split('\n')

                for line in lines:
                    line = line.strip()
                    if not line: continue

                    # Match AC
                    # AC 11.01 | Description
                    # AC 24.01MMPV | Description

                    # AC starts with AC, then some digits, dots, maybe letters, then |
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        code_part = parts[0].strip()
                        description = parts[1].strip()

                        if code_part.startswith('AC'):
                            # Extract code digits
                            # AC11.01 -> 11.01
                            # AC24.01MMPV -> 24.01MMPV
                            raw_code = code_part[2:].strip()

                            # Determine Comp ID from 2nd digit
                            # 11.01 -> Comp 1
                            # 24.01 -> Comp 4
                            # 35.01 -> Comp 5

                            if len(raw_code) >= 2 and raw_code[1].isdigit():
                                comp_id = int(raw_code[1])
                                level_digit = raw_code[0]
                                level = int(level_digit) if level_digit.isdigit() else 1

                                if comp_id in competencies:
                                    comp = competencies[comp_id]

                                    ac_code = code_part
                                    ac, created = CriticalLearning.objects.get_or_create(
                                        code=ac_code,
                                        defaults={
                                            'competency': comp,
                                            'description': description,
                                            'level': level
                                        }
                                    )
                                    if created:
                                        self.stdout.write(f"  Created AC: {ac} (Level {level})")

        except Exception as e:
            self.stderr.write(f"Error parsing PDF: {e}")

    def get_color(self, id):
        colors = [
            '#3b82f6', # Blue
            '#ef4444', # Red
            '#10b981', # Green
            '#f59e0b', # Yellow
            '#8b5cf6', # Purple
            '#ec4899', # Pink
        ]
        return colors[(id - 1) % len(colors)]
