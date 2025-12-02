from ninja import NinjaAPI, Schema, File, Form
from ninja.files import UploadedFile
from typing import List, Optional
from django.shortcuts import get_object_or_404
from core.models import Competency, CriticalLearning, Assessment, User, StudentProfile, Cohort, Activity
from django.db.models import Count, Q
from .utils.moodle_export import export_grades_csv
from .utils.moodle_import import import_moodle_csv
from .utils.student_import import import_students_csv
from django.http import HttpResponse,  Http404

api = NinjaAPI()

# Schemas
class CompetencySchema(Schema):
    id: int
    name: str
    short_code: str
    color_hex: str
    description: str

class CriticalLearningSchema(Schema):
    id: int
    code: str
    description: str
    level: int

class AssessmentSchema(Schema):
    id: int
    student_id: int
    critical_learning_id: int
    role_evaluator: str
    is_concerned: Optional[bool] = None
    frequency: Optional[str] = None
    validation_level: Optional[str] = None
    validation_status: str
    comment: str

class AssessmentCreateSchema(Schema):
    student_id: int
    critical_learning_id: int
    activity_id: int

    # Declarative (Student/Tutor)
    is_concerned: Optional[bool] = None
    frequency: Optional[str] = None # RARELY, OFTEN, SYSTEMATICALLY

    # Validation (Teacher)
    validation_level: Optional[str] = None # NOT_ACQUIRED, IN_PROGRESS, ACQUIRED, MASTERED

    comment: Optional[str] = ""

class ValidationUpdateSchema(Schema):
    validation_status: str # PENDING_INTERVIEW, VALIDATED
    validation_level: Optional[str] = None # Required if VALIDATED

# Endpoints

@api.get("/competencies", response=List[CompetencySchema])
def list_competencies(request):
    return Competency.objects.all()

@api.get("/competencies/{competency_id}/acs", response=List[CriticalLearningSchema])
def list_acs(request, competency_id: int):
    return CriticalLearning.objects.filter(competency_id=competency_id)

@api.post("/assessments", response={200: dict, 403: dict, 422: dict})
def create_assessment(request, payload: AssessmentCreateSchema):
    evaluator = request.user if request.user.is_authenticated else None
    role_evaluator = Assessment.RoleEvaluator.STUDENT # Default fallback

    if evaluator:
        if evaluator.role == User.Role.TEACHER:
            role_evaluator = Assessment.RoleEvaluator.TEACHER
        elif evaluator.role == User.Role.STUDENT:
            role_evaluator = Assessment.RoleEvaluator.STUDENT
    # TODO: Handle Tutor Logic (Magic Link) - passed via auth probably

    # Logic Verification
    if role_evaluator in [Assessment.RoleEvaluator.STUDENT, Assessment.RoleEvaluator.TUTOR]:
        # Student/Tutor CANNOT set validation_level
        if payload.validation_level:
            return 403, {"message": "Students/Tutors cannot set validation level directly."}

        # Must have is_concerned
        if payload.is_concerned is None:
             return 422, {"message": "is_concerned is required."}

        # If concerned, frequency is required (or maybe optional? Prompt says 'Must renseign frequency')
        if payload.is_concerned and not payload.frequency:
             return 422, {"message": "Frequency is required when concerned."}

        # Force None for safety
        final_validation_level = None
        final_status = Assessment.ValidationStatus.PENDING_WRITING

    elif role_evaluator == Assessment.RoleEvaluator.TEACHER:
        # Teacher sets validation level
        final_validation_level = payload.validation_level
        # If teacher sets level, assume validated? Or pending interview?
        # Prompt: "Teacher unblocks and assigns final level after interview."
        # So if Teacher is posting, it might be the final validation step.
        final_status = Assessment.ValidationStatus.VALIDATED if payload.validation_level else Assessment.ValidationStatus.PENDING_INTERVIEW

    else:
        return 403, {"message": "Unknown evaluator role."}

    assessment = Assessment.objects.create(
        student_id=payload.student_id,
        critical_learning_id=payload.critical_learning_id,
        activity_id=payload.activity_id,
        evaluator=evaluator,
        role_evaluator=role_evaluator,

        is_concerned=payload.is_concerned,
        frequency=payload.frequency,

        validation_level=final_validation_level,
        validation_status=final_status,

        comment=payload.comment,
    )
    return {"id": assessment.id}

@api.put("/assessments/{assessment_id}/validate", response={200: dict, 403: dict})
def validate_assessment(request, assessment_id: int, payload: ValidationUpdateSchema):
    # Only Teachers can validate
    if not request.user.is_authenticated or request.user.role != User.Role.TEACHER:
        return 403, {"message": "Only teachers can validate assessments."}

    assessment = get_object_or_404(Assessment, id=assessment_id)

    assessment.validation_status = payload.validation_status
    if payload.validation_level:
        assessment.validation_level = payload.validation_level

    assessment.save()
    return {"id": assessment.id, "status": assessment.validation_status, "level": assessment.validation_level}

@api.get("/student/{student_id}/dashboard")
def student_dashboard(request, student_id: int):
    """
    Returns data for the spider chart.
    Calculates progress per competency.
    Only counts VALIDATED assessments with ACQUIRED/MASTERED level.
    """
    competencies = Competency.objects.all()
    data = []

    for comp in competencies:
        acs_count = comp.critical_learnings.count()
        if acs_count == 0:
            percentage = 0
        else:
            # Count acquired/mastered ACs for this student
            # Must be VALIDATED by Teacher
            acquired_count = Assessment.objects.filter(
                student_id=student_id,
                critical_learning__competency=comp,
                validation_level__in=['ACQUIRED', 'MASTERED']
            ).values('critical_learning').distinct().count()

            percentage = (acquired_count / acs_count) * 100

        data.append({
            "competency": comp.short_code,
            "name": comp.name,
            "progress": percentage
        })

    return data

@api.get("/export/moodle")
def export_moodle(request, cohort_id: Optional[int] = None):
    csv_data = export_grades_csv(cohort_id)
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="moodle_export.csv"'
    return response

@api.post("/import/moodle/framework", response={200: dict, 400: dict})
def import_moodle_framework(request, file: UploadedFile = File(...)):
    if not file.name.endswith('.csv'):
        return 400, {"message": "File must be a CSV."}

    try:
        content = file.read()
        stats = import_moodle_csv(content)
        return stats
    except Exception as e:
        return 400, {"message": str(e)}

@api.post("/import/moodle/students", response={200: dict, 400: dict})
def import_moodle_students(
    request,
    file: UploadedFile = File(...),
    cohort_id: int = Form(...),
    current_level: str = Form(...), # BUT1, BUT2...
    cohort_year: int = Form(...)
):
    """
    Imports students from Moodle 'Participants' export (CSV).
    Required columns: Email, First name, Last name, ID number (optional but recommended).
    """
    if not file.name.endswith('.csv'):
        return 400, {"message": "File must be a CSV."}

    try:
        content = file.read()
        stats = import_students_csv(content, cohort_id, current_level, cohort_year)
        return stats
    except Exception as e:
        import traceback
        traceback.print_exc()
        return 400, {"message": str(e)}
