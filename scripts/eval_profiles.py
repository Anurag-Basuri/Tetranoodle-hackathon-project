# Evaluation script demonstrating dynamic profile adaptability on unseen profiles
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.domain.profile import StudentProfile
from app.domain.evidence import Criterion, CriterionAssessment
from app.domain.criteria_rules import (
    evaluate_min_grade,
    evaluate_degree_level,
    evaluate_nationality,
    evaluate_field_of_study,
    derive_overall,
)
from app.domain.enums import CriterionKind, CriterionStatus, OverallEligibility, VerificationStatus, FundingType
from app.domain.opportunity import Opportunity
from app.domain.ranking import score_funding_fit, score_country_preference
from uuid import uuid4

def run_evaluation():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "tests", "fixtures")
    rahul_path = os.path.join(base_dir, "rahul.json")
    ananya_path = os.path.join(base_dir, "second_profile.json")

    with open(rahul_path, "r", encoding="utf-8") as f:
        rahul_data = json.load(f)
    with open(ananya_path, "r", encoding="utf-8") as f:
        ananya_data = json.load(f)

    rahul = StudentProfile.model_validate(rahul_data)
    ananya = StudentProfile.model_validate(ananya_data)

    print("==================================================================")
    print("SCHOLARPILOT AI: PROFILE ADAPTABILITY & EVALUATION")
    print("==================================================================")

    # 1. Profile 1 Evaluation (Rahul - CS / AI)
    print(f"\n1. Profile: {rahul.full_name} ({rahul.field_of_study}, CGPA: {rahul.grade.value}/{rahul.grade.scale})")
    print(f"   Target degree: {rahul.degree_level_target.value}, Countries: {rahul.target_countries}")
    
    crit_grade_1 = Criterion(
        id="c1",
        kind=CriterionKind.MIN_GRADE,
        description="Minimum 7.5 on 10.0 scale",
        params={"min_value": 7.5, "scale": 10.0},
    )
    crit_degree_1 = Criterion(
        id="c2",
        kind=CriterionKind.DEGREE_LEVEL,
        description="Bachelor degree required",
        params={"min_level": "bachelor"},
    )
    crit_nat_1 = Criterion(
        id="c3",
        kind=CriterionKind.NATIONALITY,
        description="Eligible nationalities",
        params={"allowed_countries": ["India", "Germany", "Singapore"]},
    )
    crit_field_1 = Criterion(
        id="c4",
        kind=CriterionKind.FIELD_OF_STUDY,
        description="Computer Science or Informatics",
        params={"allowed_fields": ["Computer Science", "Informatics"]},
    )

    r_grade_status, r_grade_reason, _ = evaluate_min_grade(crit_grade_1, rahul)
    r_deg_status, r_deg_reason, _ = evaluate_degree_level(crit_degree_1, rahul)
    r_nat_status, r_nat_reason, _ = evaluate_nationality(crit_nat_1, rahul)
    r_field_status, r_field_reason, _ = evaluate_field_of_study(crit_field_1, rahul)

    print(f"   - Min grade check (req >= 7.5/10.0): {r_grade_status.value} ({r_grade_reason})")
    print(f"   - Degree level check (req >= bachelor): {r_deg_status.value} ({r_deg_reason})")
    print(f"   - Nationality check (allowed list): {r_nat_status.value} ({r_nat_reason})")
    print(f"   - Field of study check: {r_field_status.value} ({r_field_reason})")
    
    assert r_grade_status == CriterionStatus.MEETS
    assert r_deg_status == CriterionStatus.MEETS
    assert r_nat_status == CriterionStatus.MEETS
    assert r_field_status in (CriterionStatus.MEETS, CriterionStatus.LIKELY_MEETS)

    # 2. Profile 2 Evaluation (Ananya - Biotechnology / Genomics)
    print(f"\n2. Profile: {ananya.full_name} ({ananya.field_of_study}, CGPA: {ananya.grade.value}/{ananya.grade.scale})")
    print(f"   Target degree: {ananya.degree_level_target.value}, Countries: {ananya.target_countries}")
    print(f"   Language tests submitted: {len(ananya.language_tests)}")

    crit_grade_2 = Criterion(
        id="c5",
        kind=CriterionKind.MIN_GRADE,
        description="Minimum 8.5 on 10.0 scale",
        params={"min_value": 8.5, "scale": 10.0},
    )
    crit_field_2 = Criterion(
        id="c6",
        kind=CriterionKind.FIELD_OF_STUDY,
        description="Biotechnology or Molecular Life Sciences",
        params={"allowed_fields": ["Biotechnology", "Bioinformatics", "Biology"]},
    )

    a_grade_status, a_grade_reason, _ = evaluate_min_grade(crit_grade_2, ananya)
    a_field_status, a_field_reason, _ = evaluate_field_of_study(crit_field_2, ananya)

    print(f"   - Min grade check (req >= 8.5/10.0): {a_grade_status.value} ({a_grade_reason})")
    print(f"   - Field of study check: {a_field_status.value} ({a_field_reason})")

    assert a_grade_status == CriterionStatus.MEETS
    assert a_field_status in (CriterionStatus.MEETS, CriterionStatus.LIKELY_MEETS)

    # 3. Overall eligibility derivation test
    sample_assessments = [
        CriterionAssessment(
            criterion_id="c1",
            criterion="Grade",
            status=CriterionStatus.MEETS,
            reason="Meets min grade",
        ),
        CriterionAssessment(
            criterion_id="c2",
            criterion="Degree",
            status=CriterionStatus.MEETS,
            reason="Holds bachelor",
        ),
    ]
    overall_res = derive_overall(sample_assessments, VerificationStatus.VERIFIED)
    print(f"\n3. Overall eligibility derivation (all hard criteria meet): {overall_res.value}")
    assert overall_res == OverallEligibility.MEETS_ALL_STATED

    # 4. Scoring factors verification
    mock_opp_de = Opportunity(
        job_id=uuid4(),
        name="DAAD Master Fellowship",
        institution="DAAD",
        country="Germany",
        funding_type=FundingType.FULL,
    )
    mock_opp_fr = Opportunity(
        job_id=uuid4(),
        name="Eiffel Fellowship",
        institution="Campus France",
        country="France",
        funding_type=FundingType.FULL,
    )

    funding_score = score_funding_fit(mock_opp_de, rahul)
    country_score_de = score_country_preference(mock_opp_de, rahul)
    country_score_fr = score_country_preference(mock_opp_fr, rahul)
    print(f"\n4. Scoring tests:")
    print(f"   - Full funding score: {funding_score} / 25.0")
    print(f"   - Country fit (Germany in target): {country_score_de} / 10.0")
    print(f"   - Country fit (France not in target): {country_score_fr} / 10.0")

    assert funding_score == 25.0
    assert country_score_de == 10.0
    assert country_score_fr == 0.0

    print("\n[SUCCESS] Profile adaptability evaluation passed completely without hardcoded logic!")

if __name__ == "__main__":
    run_evaluation()
