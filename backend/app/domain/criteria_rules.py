from datetime import date
from typing import List, Optional
from app.domain.enums import CriterionKind, CriterionStatus, DegreeLevel, OverallEligibility, VerificationStatus
from app.domain.evidence import Criterion, CriterionAssessment
from app.domain.profile import StudentProfile

# Ordinal ranking for degree levels
DEGREE_ORDER = {
    DegreeLevel.BACHELOR: 1,
    DegreeLevel.MASTER: 2,
    DegreeLevel.PHD: 3,
}

def normalize_degree_level(raw: Optional[str]) -> Optional[DegreeLevel]:
    # Normalizes extracted degree strings to standard DegreeLevel enum
    if not raw:
        return None
    s = raw.lower().strip()
    if "phd" in s or "doctor" in s:
        return DegreeLevel.PHD
    if "master" in s or "msc" in s or "m.sc" in s or "postgraduate" in s:
        return DegreeLevel.MASTER
    if "bachelor" in s or "bsc" in s or "b.sc" in s or "undergraduate" in s or "first degree" in s or "b.tech" in s:
        return DegreeLevel.BACHELOR
    try:
        return DegreeLevel(s)
    except ValueError:
        return None

def evaluate_degree_level(criterion: Criterion, profile: StudentProfile) -> tuple[CriterionStatus, str, Optional[str]]:
    # Compare student degree against required minimum
    min_level_str = criterion.params.get("min_level")
    if not min_level_str:
        return CriterionStatus.UNKNOWN, "No degree level requirement specified", None

    min_level = normalize_degree_level(min_level_str)
    if not min_level:
        return CriterionStatus.NEEDS_REVIEW, f"Degree requirement '{min_level_str}' needs review", "Verify program prerequisites"

    if not profile.degree_level_held:
        return CriterionStatus.UNKNOWN, "Student held degree level is missing", "Provide current degree status"

    held_order = DEGREE_ORDER.get(profile.degree_level_held, 0)
    req_order = DEGREE_ORDER.get(min_level, 0)

    if held_order >= req_order:
        return CriterionStatus.MEETS, f"Held degree ({profile.degree_level_held.value}) satisfies requirement ({min_level.value})", None
    return CriterionStatus.DOES_NOT_MEET, f"Held degree ({profile.degree_level_held.value}) is below requirement ({min_level.value})", None

def evaluate_field_of_study(criterion: Criterion, profile: StudentProfile) -> tuple[CriterionStatus, str, Optional[str]]:
    # Compare student field of study against allowed fields
    allowed = criterion.params.get("allowed_fields", [])
    if not allowed or not profile.field_of_study:
        return CriterionStatus.NEEDS_REVIEW, "Field of study needs manual review", "Verify program curriculum match"

    student_field = profile.field_of_study.strip().lower()
    allowed_norm = [f.strip().lower() for f in allowed]

    # Exact or substring match in allowed fields
    for target in allowed_norm:
        if target in student_field or student_field in target:
            return CriterionStatus.LIKELY_MEETS, f"Field '{profile.field_of_study}' closely matches accepted discipline '{target}'", None

    return CriterionStatus.NEEDS_REVIEW, f"Field '{profile.field_of_study}' requires review against required fields", "Check program syllabus"

def evaluate_min_grade(criterion: Criterion, profile: StudentProfile) -> tuple[CriterionStatus, str, Optional[str]]:
    # Compare grades only when scales match exactly
    if not profile.grade:
        return CriterionStatus.UNKNOWN, "Student GPA or percentage not provided", "Add CGPA to profile"

    min_val = criterion.params.get("min_value")
    req_scale = criterion.params.get("scale")

    if min_val is None or req_scale is None:
        return CriterionStatus.NEEDS_REVIEW, "University specifies grade rules in text", "Check the university grade conversion rule"

    # Avoid automated cross scale conversions like 8.2/10 to US 4.0
    if abs(float(req_scale) - float(profile.grade.scale)) > 0.01:
        return CriterionStatus.NEEDS_REVIEW, f"Scale mismatch (student has scale {profile.grade.scale}, program requires scale {req_scale})", "Check the university grade conversion rule"

    if float(profile.grade.value) >= float(min_val):
        return CriterionStatus.MEETS, f"Grade {profile.grade.value}/{profile.grade.scale} meets required {min_val}/{req_scale}", None

    return CriterionStatus.DOES_NOT_MEET, f"Grade {profile.grade.value}/{profile.grade.scale} is below required {min_val}/{req_scale}", None

def evaluate_language(criterion: Criterion, profile: StudentProfile) -> tuple[CriterionStatus, str, Optional[str]]:
    # Compare language test scores and flag exemptions
    exemptions = criterion.params.get("exemptions", [])
    exemption_note = f"Exemption ممکن: {exemptions[0]}" if exemptions else None

    if not profile.language_tests:
        action = "Provide IELTS/TOEFL scores" if not exemptions else f"Provide English scores or claim exemption: {exemptions[0]}"
        return CriterionStatus.UNKNOWN, "No English language test recorded", action

    tests_accepted = [t.lower() for t in criterion.params.get("tests_accepted", [])]
    min_score = criterion.params.get("min_score")

    for test in profile.language_tests:
        if not tests_accepted or test.test.lower() in tests_accepted:
            if min_score is not None and test.score is not None:
                if test.score >= float(min_score):
                    return CriterionStatus.MEETS, f"{test.test} score {test.score} meets minimum {min_score}", None
                return CriterionStatus.DOES_NOT_MEET, f"{test.test} score {test.score} is below minimum {min_score}", "Retake exam"
            return CriterionStatus.LIKELY_MEETS, f"{test.test} test submitted", None

    return CriterionStatus.UNKNOWN, "Supplied language test not listed among accepted tests", "Confirm accepted test list"

def evaluate_nationality(criterion: Criterion, profile: StudentProfile) -> tuple[CriterionStatus, str, Optional[str]]:
    # Compare student nationality against eligible countries
    student_nat = profile.nationality.strip().lower()
    excluded = [c.strip().lower() for c in criterion.params.get("excluded", [])]

    if student_nat in excluded:
        return CriterionStatus.DOES_NOT_MEET, f"Applicants from {profile.nationality} are not eligible", None

    eligible = [c.strip().lower() for c in criterion.params.get("eligible", [])]
    if eligible:
        if student_nat in eligible:
            return CriterionStatus.MEETS, f"Citizens of {profile.nationality} are eligible", None
        return CriterionStatus.DOES_NOT_MEET, f"{profile.nationality} is not in the list of eligible nationalities", None

    if criterion.params.get("international_ok", True):
        return CriterionStatus.MEETS, "Open to international students", None

    return CriterionStatus.NEEDS_REVIEW, "Nationality rules are ambiguous", "Review citizenship requirements"

def evaluate_deadline(criterion: Criterion, today: Optional[date] = None) -> tuple[CriterionStatus, str, Optional[str]]:
    # Check application deadline feasibility
    today = today or date.today()
    deadline_val = criterion.params.get("date")

    if not deadline_val:
        return CriterionStatus.UNKNOWN, "Application deadline not specified", "Check official portal for round dates"

    try:
        if isinstance(deadline_val, str):
            deadline_date = date.fromisoformat(deadline_val)
        else:
            deadline_date = deadline_val
    except ValueError:
        return CriterionStatus.UNKNOWN, f"Could not parse deadline '{deadline_val}'", "Verify date on website"

    if deadline_date < today:
        return CriterionStatus.DOES_NOT_MEET, f"Deadline passed on {deadline_date} (closed)", "Check next intake dates"

    return CriterionStatus.MEETS, f"Deadline is {deadline_date}", "Confirm on the official page"

def evaluate_criterion(criterion: Criterion, profile: StudentProfile, today: Optional[date] = None) -> CriterionAssessment:
    # Run appropriate evaluator based on criterion kind
    today = today or date.today()

    # Rule: Hard criteria with quote_verified=False must be demoted to unknown
    if criterion.is_hard and criterion.evidence and not criterion.evidence.quote_verified:
        return CriterionAssessment(
            criterion_id=criterion.id,
            criterion=criterion.description,
            required_value=criterion.required_value,
            student_value=None,
            status=CriterionStatus.UNKNOWN,
            reason="Official evidence excerpt could not be verified in source page",
            next_action="Re-verify against official web text",
            source_url=criterion.evidence.source_url if criterion.evidence else None,
            source_excerpt=criterion.evidence.source_excerpt if criterion.evidence else None,
            verified_at=criterion.evidence.verified_at if criterion.evidence else None,
        )

    # Evaluate by kind
    if criterion.kind == CriterionKind.DEGREE_LEVEL:
        status, reason, action = evaluate_degree_level(criterion, profile)
        student_val = profile.degree_level_held.value if profile.degree_level_held else None
    elif criterion.kind == CriterionKind.FIELD_OF_STUDY:
        status, reason, action = evaluate_field_of_study(criterion, profile)
        student_val = profile.field_of_study
    elif criterion.kind == CriterionKind.MIN_GRADE:
        status, reason, action = evaluate_min_grade(criterion, profile)
        student_val = f"{profile.grade.value}/{profile.grade.scale}" if profile.grade else None
    elif criterion.kind == CriterionKind.LANGUAGE:
        status, reason, action = evaluate_language(criterion, profile)
        student_val = ", ".join([f"{t.test}:{t.score}" for t in profile.language_tests]) if profile.language_tests else None
    elif criterion.kind == CriterionKind.NATIONALITY:
        status, reason, action = evaluate_nationality(criterion, profile)
        student_val = profile.nationality
    elif criterion.kind == CriterionKind.DEADLINE:
        status, reason, action = evaluate_deadline(criterion, today)
        student_val = None
    else:
        # Fallback for documents or generic text criteria
        status = CriterionStatus.NEEDS_REVIEW
        reason = "Non-standard criterion requires student review"
        action = "Check full university guidelines"
        student_val = None

    return CriterionAssessment(
        criterion_id=criterion.id,
        criterion=criterion.description,
        required_value=criterion.required_value,
        student_value=student_val,
        status=status,
        reason=reason,
        next_action=action,
        source_url=criterion.evidence.source_url if criterion.evidence else None,
        source_excerpt=criterion.evidence.source_excerpt if criterion.evidence else None,
        verified_at=criterion.evidence.verified_at if criterion.evidence else None,
    )

def derive_overall(assessments: List[CriterionAssessment], verification_status: VerificationStatus) -> OverallEligibility:
    # Rule 1: not_eligible if any criterion does not meet
    for a in assessments:
        if a.status == CriterionStatus.DOES_NOT_MEET:
            return OverallEligibility.NOT_ELIGIBLE

    # Rule 2: meets_all_stated if verified and all meet
    if verification_status == VerificationStatus.VERIFIED:
        if all(a.status == CriterionStatus.MEETS for a in assessments) and len(assessments) > 0:
            return OverallEligibility.MEETS_ALL_STATED

    # Rule 3: likely_eligible if all are meets or likely_meets
    if all(a.status in (CriterionStatus.MEETS, CriterionStatus.LIKELY_MEETS) for a in assessments) and len(assessments) > 0:
        return OverallEligibility.LIKELY_ELIGIBLE

    # Rule 4: needs_info otherwise
    return OverallEligibility.NEEDS_INFO
