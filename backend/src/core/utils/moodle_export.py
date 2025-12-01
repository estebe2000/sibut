import csv
from io import StringIO
from core.models import Assessment

def export_grades_csv(cohort_id=None):
    """
    Export grades in a format compatible with Moodle (CSV).
    Moodle CSV import usually requires: username, course, grade, etc.
    This is a basic implementation.
    """
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(['username', 'competency_code', 'ac_code', 'value', 'comment'])

    assessments = Assessment.objects.all()
    if cohort_id:
        assessments = assessments.filter(student__student_profile__cohort_id=cohort_id)

    for assessment in assessments:
        writer.writerow([
            assessment.student.username,
            assessment.critical_learning.competency.short_code,
            assessment.critical_learning.code,
            assessment.value,
            assessment.comment
        ])

    return output.getvalue()
