from datetime import date, timedelta
from app.domain.enums import DegreeLevel, CriterionKind, CriterionStatus, OverallEligibility, VerificationStatus
from app.domain.profile import StudentProfile, Grade, LanguageTest
from app.domain.evidence import Criterion, EvidenceRef
from app.domain.criteria_rules import evaluate_criterion, derive_overall

def make_profile():
    # Helper to construct Rahul's base profile
    return StudentProfile(
        full_name="Rahul Sharma",
        nationality="India",
        degree_level_held=DegreeLevel.BACHELOR,
        degree_level_target=DegreeLevel.MASTER,
        field_of_study="Computer Science",
        grade=Grade(value=8.2, scale=10.0),
        language_tests=[LanguageTest(test="IELTS", score=7.5)],
        target_countries=["Germany", "Canada"],
        needs_funding=True,
    )

def test_grade_evaluation_scale_mismatch():
    # 8.2 on 10 scale vs 3.0 on 4.0 scale must return needs_review
    profile = make_profile()
    criterion = Criterion(
        id="c1",
        kind=CriterionKind.MIN_GRADE,
        description="Minimum GPA of 3.0 on a 4.0 scale",
        params={"min_value": 3.0, "scale": 4.0},
    )
    assessment = evaluate_criterion(criterion, profile)
    assert assessment.status == CriterionStatus.NEEDS_REVIEW
    assert "Scale mismatch" in assessment.reason

def test_grade_evaluation_same_scale():
    # 8.2 on 10 scale meets 7.5 on 10 scale
    profile = make_profile()
    criterion = Criterion(
        id="c2",
        kind=CriterionKind.MIN_GRADE,
        description="Minimum 7.5 CGPA out of 10",
        params={"min_value": 7.5, "scale": 10.0},
    )
    assessment = evaluate_criterion(criterion, profile)
    assert assessment.status == CriterionStatus.MEETS

def test_degree_level_ordinal():
    # Bachelor held meets Bachelor required
    profile = make_profile()
    criterion = Criterion(
        id="c3",
        kind=CriterionKind.DEGREE_LEVEL,
        description="Must hold Bachelor degree",
        params={"min_level": "bachelor"},
    )
    assessment = evaluate_criterion(criterion, profile)
    assert assessment.status == CriterionStatus.MEETS

def test_nationality_matching():
    # Explicitly eligible nationality meets
    profile = make_profile()
    criterion = Criterion(
        id="c4",
        kind=CriterionKind.NATIONALITY,
        description="Open to applicants from India",
        params={"eligible": ["India", "Nepal"]},
    )
    assessment = evaluate_criterion(criterion, profile)
    assert assessment.status == CriterionStatus.MEETS

def test_nationality_excluded():
    # Explicitly excluded nationality fails
    profile = make_profile()
    criterion = Criterion(
        id="c5",
        kind=CriterionKind.NATIONALITY,
        description="Not open to Indian applicants",
        params={"excluded": ["India"]},
    )
    assessment = evaluate_criterion(criterion, profile)
    assert assessment.status == CriterionStatus.DOES_NOT_MEET

def test_deadline_expired():
    # Past deadline must return does_not_meet
    profile = make_profile()
    past_date = str(date.today() - timedelta(days=5))
    criterion = Criterion(
        id="c6",
        kind=CriterionKind.DEADLINE,
        description="Application deadline",
        params={"date": past_date},
    )
    assessment = evaluate_criterion(criterion, profile)
    assert assessment.status == CriterionStatus.DOES_NOT_MEET

def test_unverified_quote_demotion():
    # Hard criteria with unverified quote must be demoted to unknown
    profile = make_profile()
    criterion = Criterion(
        id="c7",
        kind=CriterionKind.MIN_GRADE,
        description="Minimum 7.0 CGPA",
        params={"min_value": 7.0, "scale": 10.0},
        is_hard=True,
        evidence=EvidenceRef(
            source_id="11111111-1111-1111-1111-111111111111",
            source_url="https://example.edu/admissions",
            source_excerpt="Minimum 7.0 CGPA required",
            verified_at="2026-10-22T00:00:00Z",
            quote_verified=False,
        ),
    )
    assessment = evaluate_criterion(criterion, profile)
    assert assessment.status == CriterionStatus.UNKNOWN

def test_derive_overall_rules():
    # Test derive_overall transitions
    profile = make_profile()
    c_pass = Criterion(id="cp", kind=CriterionKind.DEGREE_LEVEL, description="Degree", params={"min_level": "bachelor"})
    c_fail = Criterion(id="cf", kind=CriterionKind.NATIONALITY, description="Nationality", params={"excluded": ["India"]})

    a_pass = evaluate_criterion(c_pass, profile)
    a_fail = evaluate_criterion(c_fail, profile)

    # Any does_not_meet makes the overall status not_eligible
    assert derive_overall([a_pass, a_fail], VerificationStatus.VERIFIED) == OverallEligibility.NOT_ELIGIBLE

    # All meets on verified source gives meets_all_stated
    assert derive_overall([a_pass], VerificationStatus.VERIFIED) == OverallEligibility.MEETS_ALL_STATED

    # All meets on unverified source gives likely_eligible
    assert derive_overall([a_pass], VerificationStatus.UNVERIFIED) == OverallEligibility.LIKELY_ELIGIBLE
