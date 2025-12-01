from ninja import NinjaAPI, Schema
from typing import List, Optional
from django.shortcuts import get_object_or_404
from core.models import Competency, CriticalLearning, Assessment, User, StudentProfile, Cohort, Activity
from django.db.models import Count, Q
from .utils.moodle_export import export_grades_csv
from django.http import HttpResponse

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
    value: str
    comment: str

class AssessmentCreateSchema(Schema):
    student_id: int
    critical_learning_id: int
    activity_id: int
    value: str
    comment: Optional[str] = ""

# Endpoints

@api.get("/competencies", response=List[CompetencySchema])
def list_competencies(request):
    return Competency.objects.all()

@api.get("/competencies/{competency_id}/acs", response=List[CriticalLearningSchema])
def list_acs(request, competency_id: int):
    return CriticalLearning.objects.filter(competency_id=competency_id)

@api.post("/assessments")
def create_assessment(request, payload: AssessmentCreateSchema):
    assessment = Assessment.objects.create(
        student_id=payload.student_id,
        critical_learning_id=payload.critical_learning_id,
        activity_id=payload.activity_id,
        value=payload.value,
        comment=payload.comment,
        evaluator=request.user if request.user.is_authenticated else None
    )
    return {"id": assessment.id}

@api.get("/student/{student_id}/dashboard")
def student_dashboard(request, student_id: int):
    """
    Returns data for the spider chart.
    Calculates progress per competency.
    """
    competencies = Competency.objects.all()
    data = []

    for comp in competencies:
        acs_count = comp.critical_learnings.count()
        if acs_count == 0:
            percentage = 0
        else:
            # Count acquired/mastered ACs for this student
            acquired_count = Assessment.objects.filter(
                student_id=student_id,
                critical_learning__competency=comp,
                value__in=['ACQUIRED', 'MASTERED']
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
