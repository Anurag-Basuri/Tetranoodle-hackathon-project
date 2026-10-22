import pytest
from app.domain.enums import DegreeLevel, CriterionStatus, OverallEligibility
from app.domain.profile import StudentProfile, Grade


def test_domain_model_creation():
    profile = StudentProfile(
        full_name="Rahul Sharma",
        nationality="India",
        degree_level_target=DegreeLevel.MASTER,
        grade=Grade(value=8.2, scale=10.0),
        target_countries=["Canada", "Germany", "Singapore"],
    )
    assert profile.full_name == "Rahul Sharma"
    assert profile.grade.value == 8.2
    assert profile.degree_level_target == DegreeLevel.MASTER


def test_enums():
    assert CriterionStatus.MEETS == "meets"
    assert OverallEligibility.NOT_ELIGIBLE == "not_eligible"
