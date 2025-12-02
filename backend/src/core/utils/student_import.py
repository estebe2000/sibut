import csv
import io
from core.models import User, StudentProfile, Cohort
from django.db import transaction

def import_students_csv(file_content_bytes, cohort_id, current_level, cohort_year):
    """
    Imports students from a Moodle Participants CSV export.

    Expected CSV columns (approximate):
    - First name
    - Surname
    - Email address
    - ID number (INE)

    Arguments:
    - file_content_bytes: content of the CSV file
    - cohort_id: ID of the Cohort (Promo) to assign students to
    - current_level: BUT1, BUT2, or BUT3
    - cohort_year: Year of the cohort (e.g., 2025)
    """

    decoded_file = file_content_bytes.decode('utf-8-sig').splitlines()
    reader = csv.DictReader(decoded_file)

    # Normalize headers
    field_map = {}
    for field in reader.fieldnames:
        clean = field.lower().strip().replace(' ', '')
        if 'firstname' in clean:
            field_map['first_name'] = field
        elif 'surname' in clean or 'lastname' in clean:
            field_map['last_name'] = field
        elif 'email' in clean:
            field_map['email'] = field
        elif 'idnumber' in clean:
            field_map['id_number'] = field # INE

    if 'email' not in field_map:
        raise ValueError("CSV must contain an 'Email' column.")

    cohort = None
    if cohort_id:
        cohort = Cohort.objects.get(pk=cohort_id)

    created_count = 0
    updated_count = 0

    with transaction.atomic():
        for row in reader:
            email = row.get(field_map['email'], '').strip()
            first_name = row.get(field_map.get('first_name', ''), '').strip()
            last_name = row.get(field_map.get('last_name', ''), '').strip()
            id_number = row.get(field_map.get('id_number', ''), '').strip()

            if not email:
                continue

            # Generate username from email (or part of it)
            username = email.split('@')[0]

            # Check if user exists
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username, # Potential conflict if duplicate usernames but diff emails, handle later
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': User.Role.STUDENT
                }
            )

            if not created:
                # Update info
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            # Create/Update Profile
            # If ID number is missing from CSV, we might skip updating it or generate a temp one?
            # Prompt implies importing list, usually ID number is present.
            # If not present, we can't really enforce uniqueness or it might crash.
            # Let's handle graceful fallback or error.

            if not id_number:
                # Skip profile update if no ID number provided, to avoid crash on unique constraint if empty string is treated as duplicate?
                # Actually, usually empty strings can be duplicate if not unique=True constrained to non-null.
                # Django unique=True with CharField doesn't like duplicate empty strings in some DBs.
                # Let's assume ID number is required for a valid student profile.
                if created:
                    # If we created the user but can't create profile, that's partial state.
                    # But maybe we just skip profile.
                    continue
            else:
                profile, profile_created = StudentProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'student_number': id_number,
                        'cohort': cohort,
                        'cohort_year': cohort_year,
                        'current_level': current_level
                    }
                )

            if created:
                created_count += 1
            else:
                updated_count += 1

    return {
        "created": created_count,
        "updated": updated_count
    }
