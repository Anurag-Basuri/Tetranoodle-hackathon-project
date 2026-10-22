import uuid
from datetime import date, timedelta
from app.domain.enums import DegreeLevel, FundingType, VerificationStatus, OverallEligibility
from app.domain.profile import StudentProfile, Grade
from app.domain.opportunity import Opportunity
from app.domain.ranking import compute_opportunity_score, rank_opportunities

def make_profile():
    return StudentProfile(
        full_name="Rahul Sharma",
        nationality="India",
        degree_level_held=DegreeLevel.BACHELOR,
        degree_level_target=DegreeLevel.MASTER,
        field_of_study="Computer Science",
        grade=Grade(value=8.2, scale=10.0),
        target_countries=["Germany", "Canada"],
        needs_funding=True,
    )

def test_ranking_score_computation():
    profile = make_profile()
    opp = Opportunity(
        job_id=uuid.uuid4(),
        name="DAAD Master Scholarship",
        institution="TU Munich",
        country="Germany",
        funding_type=FundingType.FULL,
        deadline=date.today() + timedelta(days=90),
        verification_status=VerificationStatus.VERIFIED,
    )

    total, breakdown = compute_opportunity_score(opp, [], profile, relevance_score=1.0)

    # Full funding gets 25, Germany gets 10, >60 days gets 10, relevance gets 20
    assert breakdown["funding"] == 25.0
    assert breakdown["country"] == 10.0
    assert breakdown["deadline"] == 10.0
    assert breakdown["relevance"] == 20.0
    assert total > 70.0

def test_rank_diversity_cap():
    # Verify max 2 per institution constraint
    profile = make_profile()
    opps = []
    assessments_by_opp = {}
    overall_by_opp = {}

    for i in range(4):
        opp = Opportunity(
            job_id=uuid.uuid4(),
            name=f"Scholarship {i}",
            institution="University of Waterloo",
            country="Canada",
            funding_type=FundingType.FULL,
            deadline=date.today() + timedelta(days=70),
        )
        opps.append(opp)
        assessments_by_opp[str(opp.id)] = []
        overall_by_opp[str(opp.id)] = OverallEligibility.LIKELY_ELIGIBLE

    # Add 2 more from another university
    for i in range(2):
        opp = Opportunity(
            job_id=uuid.uuid4(),
            name=f"Scholarship TUM {i}",
            institution="TU Munich",
            country="Germany",
            funding_type=FundingType.FULL,
            deadline=date.today() + timedelta(days=70),
        )
        opps.append(opp)
        assessments_by_opp[str(opp.id)] = []
        overall_by_opp[str(opp.id)] = OverallEligibility.LIKELY_ELIGIBLE

    ranked = rank_opportunities(opps, assessments_by_opp, overall_by_opp, profile)

    waterloo_count = sum(1 for r in ranked if any(o.institution == "University of Waterloo" for o in opps if o.id == r.opportunity_id))
    # Institution cap allows at most 2
    assert waterloo_count <= 2
    assert len(ranked) <= 5
