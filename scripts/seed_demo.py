# Seed script to populate demo data for Rahul Sharma in Neon DB
import asyncio
import json
import os
import sys
from datetime import datetime, date
from uuid import UUID

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.infrastructure.db import init_db, AsyncSessionLocal
from app.infrastructure.models import ResearchJobModel
from app.infrastructure.repositories.profiles import ProfileRepository
from app.infrastructure.repositories.jobs import JobRepository
from app.infrastructure.repositories.events import EventRepository
from app.infrastructure.repositories.opportunities import OpportunityRepository
from app.domain.enums import (
    JobStatus,
    AgentName,
    FundingType,
    OpportunityKind,
    VerificationStatus,
    CriterionStatus,
    OverallEligibility,
)
from app.domain.opportunity import Opportunity, RankedOpportunity
from app.domain.evidence import CriterionAssessment

async def seed_demo():
    print("Initializing database...")
    await init_db()

    fixture_path = os.path.join(os.path.dirname(__file__), "..", "backend", "tests", "fixtures", "rahul.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        profile_data = json.load(f)

    async with AsyncSessionLocal() as session:
        profile_repo = ProfileRepository(session)
        job_repo = JobRepository(session)
        event_repo = EventRepository(session)
        opp_repo = OpportunityRepository(session)

        # 1. Create or load Rahul's demo profile
        import secrets
        access_token = secrets.token_urlsafe(32)
        profile_model = await profile_repo.create(profile_data, access_token)
        profile_id = profile_model.id
        print(f"Created demo profile ID: {profile_id}")
        print(f"Capability access token: {access_token}")

        # 2. Create a completed research job
        job = await job_repo.create(
            profile_id=profile_id,
            params={"countries": ["Germany", "Canada", "Singapore"], "max_candidates": 10},
            profile_snapshot=profile_data,
        )
        job_id = job.id
        print(f"Created demo research job ID: {job_id}")

        job_uuid = UUID(job_id)

        # 3. Define realistic verified opportunities
        opp1 = Opportunity(
            job_id=job_uuid,
            name="DAAD Master's Studies Scholarships for All Academic Disciplines",
            institution="German Academic Exchange Service (DAAD)",
            country="Germany",
            official_url="https://www.daad.de/en/study-and-research-in-germany/scholarships/",
            funding_type=FundingType.FULL,
            funding_detail="Comprehensive scholarship covering monthly living stipend (934 EUR), health insurance, and travel allowance.",
            kind=OpportunityKind.SCHOLARSHIP,
            verification_status=VerificationStatus.VERIFIED,
            deadline=date(2026, 11, 15),
            application_url="https://portal.daad.de/irj/portal",
            application_steps=[
                "Register on the DAAD online portal",
                "Upload Bachelor degree certificate and transcript",
                "Submit letter of motivation and CV",
                "Provide proof of English or German language proficiency",
            ],
        )

        opp2 = Opportunity(
            job_id=job_uuid,
            name="Ontario Graduate Scholarship (OGS)",
            institution="University of Toronto",
            country="Canada",
            official_url="https://www.sgs.utoronto.ca/awards/ontario-graduate-scholarship/",
            funding_type=FundingType.FULL,
            funding_detail="Merit-based scholarship valued at up to $15,000 CAD per year for graduate students.",
            kind=OpportunityKind.SCHOLARSHIP,
            verification_status=VerificationStatus.VERIFIED,
            deadline=date(2026, 12, 1),
            application_url="https://www.sgs.utoronto.ca/awards/apply-online",
            application_steps=[
                "Complete the U of T online OGS application",
                "Submit two academic letters of reference",
                "Attach official transcripts from all post-secondary institutions",
            ],
        )

        opp3 = Opportunity(
            job_id=job_uuid,
            name="TUM International Master Scholarship",
            institution="Technical University of Munich",
            country="Germany",
            official_url="https://www.tum.de/en/studies/fees-and-financial-aid/scholarships",
            funding_type=FundingType.PARTIAL,
            funding_detail="Financial support for qualified international master students with outstanding academic records at TUM.",
            kind=OpportunityKind.SCHOLARSHIP,
            verification_status=VerificationStatus.VERIFIED,
            deadline=date(2026, 10, 31),
            application_url="https://campus.tum.de",
            application_steps=[
                "Submit admission letter for a TUM Master program",
                "Provide bank statement and justification for financial aid",
                "Submit academic transcript showing min 2.5 in German scale",
            ],
        )

        opp4 = Opportunity(
            job_id=job_uuid,
            name="NUS Master of Computing Graduate Scholarship",
            institution="National University of Singapore",
            country="Singapore",
            official_url="https://www.comp.nus.edu.sg/programmes/pg/mcomp-fa/scholarship/",
            funding_type=FundingType.TUITION_ONLY,
            funding_detail="Tuition fee grant awarded to high-achieving international applicants admitted into the Master of Computing programme.",
            kind=OpportunityKind.PROGRAM_WITH_FUNDING,
            verification_status=VerificationStatus.VERIFIED,
            deadline=date(2027, 1, 15),
            application_url="https://gradapp.nus.edu.sg",
            application_steps=[
                "Submit online application via NUS Graduate Application portal",
                "Upload resume and academic credentials",
                "Provide statement of purpose outlining research interests",
            ],
        )

        opp5 = Opportunity(
            job_id=job_uuid,
            name="Vector Institute Master's Scholarship in AI",
            institution="Vector Institute / University of Waterloo",
            country="Canada",
            official_url="https://vectorinstitute.ai/aimasters/",
            funding_type=FundingType.FULL,
            funding_detail="Prestigious $17,500 CAD scholarship recognizing top-tier students entering AI-related master programs in Ontario.",
            kind=OpportunityKind.SCHOLARSHIP,
            verification_status=VerificationStatus.VERIFIED,
            deadline=date(2026, 11, 30),
            application_url="https://vectorinstitute.ai/apply",
            application_steps=[
                "Apply to an AI-recognized graduate program at University of Waterloo",
                "Obtain faculty nomination for Vector Scholarship",
                "Submit statement detailing interest in machine learning research",
            ],
        )

        opportunities = [opp1, opp2, opp3, opp4, opp5]
        await opp_repo.save_opportunities(job_id, opportunities)

        # 4. Save criteria assessments
        assessments_by_opp = {}
        overall_by_opp = {}

        for opp in opportunities:
            opp_id = str(opp.id)
            ass_list = [
                CriterionAssessment(
                    criterion_id=f"{opp_id}:degree_level:1",
                    criterion="Degree Level",
                    required_value="Bachelor degree in relevant field",
                    student_value="bachelor",
                    status=CriterionStatus.MEETS,
                    reason="Student holds recognized Bachelor in Computer Science",
                    source_url=opp.official_url,
                    source_excerpt="Applicants must possess an accredited first university degree.",
                    verified_at=datetime.utcnow(),
                ),
                CriterionAssessment(
                    criterion_id=f"{opp_id}:min_grade:1",
                    criterion="Minimum Grade Requirement",
                    required_value=">= 7.5 / 10.0 or equivalent",
                    student_value="8.2 / 10.0",
                    status=CriterionStatus.MEETS,
                    reason="Student CGPA (8.2/10.0) comfortably satisfies requirement",
                    source_url=opp.official_url,
                    source_excerpt="A minimum GPA of 3.0/4.0 or 75% aggregate in undergraduate studies is required.",
                    verified_at=datetime.utcnow(),
                ),
                CriterionAssessment(
                    criterion_id=f"{opp_id}:field_of_study:1",
                    criterion="Field of Study",
                    required_value="Computer Science, Informatics, or related engineering",
                    student_value="Computer Science",
                    status=CriterionStatus.MEETS,
                    reason="Major matches prerequisite program field exactly",
                    source_url=opp.official_url,
                    source_excerpt="Eligible fields: Computer Science, Software Engineering, AI, and related disciplines.",
                    verified_at=datetime.utcnow(),
                ),
                CriterionAssessment(
                    criterion_id=f"{opp_id}:nationality:1",
                    criterion="Nationality Eligibility",
                    required_value="International applicants eligible",
                    student_value="India",
                    status=CriterionStatus.MEETS,
                    reason="Open to candidates from partner countries including India",
                    source_url=opp.official_url,
                    source_excerpt="Applications are open to graduates from all countries worldwide.",
                    verified_at=datetime.utcnow(),
                ),
                CriterionAssessment(
                    criterion_id=f"{opp_id}:language:1",
                    criterion="English Proficiency",
                    required_value="IELTS 6.5+ or TOEFL 90+",
                    student_value="No test submitted",
                    status=CriterionStatus.UNKNOWN,
                    reason="No language test scores provided in intake profile",
                    next_action="Submit official IELTS Academic score of at least 6.5 or request medium-of-instruction certificate",
                    source_url=opp.official_url,
                    source_excerpt="English language requirement: IELTS minimum band score 6.5 overall.",
                    verified_at=datetime.utcnow(),
                ),
            ]
            assessments_by_opp[opp_id] = ass_list
            overall_by_opp[opp_id] = OverallEligibility.LIKELY_ELIGIBLE

        await opp_repo.save_assessments(job_id, assessments_by_opp, overall_by_opp)

        # 5. Save rankings
        rankings = [
            RankedOpportunity(
                opportunity_id=opp1.id,
                rank=1,
                score=87.5,
                score_breakdown={
                    "funding_fit": 25.0,
                    "academic_fit": 25.0,
                    "program_relevance": 18.0,
                    "country_preference": 10.0,
                    "deadline_feasibility": 4.0,
                    "evidence_confidence": 5.5,
                },
                overall=OverallEligibility.LIKELY_ELIGIBLE,
                rationale="Highest funding fit with complete living stipend coverage in Germany, matching Rahul's top country choice and CS background.",
                trade_offs=["Requires early application submission before mid-November."],
                next_actions=["Obtain IELTS certificate and prepare DAAD motivation letter."],
            ),
            RankedOpportunity(
                opportunity_id=opp5.id,
                rank=2,
                score=84.0,
                score_breakdown={
                    "funding_fit": 25.0,
                    "academic_fit": 23.0,
                    "program_relevance": 19.0,
                    "country_preference": 10.0,
                    "deadline_feasibility": 4.0,
                    "evidence_confidence": 3.0,
                },
                overall=OverallEligibility.LIKELY_ELIGIBLE,
                rationale="Vector Institute scholarship offers top-tier AI prestige and full stipend in Canada, aligning directly with Rahul's AI project interests.",
                trade_offs=["Requires concurrent admission to an eligible Ontario university."],
                next_actions=["Submit graduate school application to University of Waterloo."],
            ),
            RankedOpportunity(
                opportunity_id=opp2.id,
                rank=3,
                score=81.5,
                score_breakdown={
                    "funding_fit": 25.0,
                    "academic_fit": 22.0,
                    "program_relevance": 16.0,
                    "country_preference": 10.0,
                    "deadline_feasibility": 4.0,
                    "evidence_confidence": 4.5,
                },
                overall=OverallEligibility.LIKELY_ELIGIBLE,
                rationale="Generous funding support at a global top 20 institution (U of T) in Canada.",
                trade_offs=["High competition among international graduate applicants."],
                next_actions=["Request two academic references from undergraduate faculty."],
            ),
            RankedOpportunity(
                opportunity_id=opp3.id,
                rank=4,
                score=72.0,
                score_breakdown={
                    "funding_fit": 15.0,
                    "academic_fit": 24.0,
                    "program_relevance": 16.0,
                    "country_preference": 10.0,
                    "deadline_feasibility": 4.0,
                    "evidence_confidence": 3.0,
                },
                overall=OverallEligibility.LIKELY_ELIGIBLE,
                rationale="Excellent engineering prestige at TUM with no tuition fees in Bavaria.",
                trade_offs=["Partial financial stipend only; requires supplementary living expense proof."],
                next_actions=["Prepare blocked bank account or proof of financial sponsorship."],
            ),
            RankedOpportunity(
                opportunity_id=opp4.id,
                rank=5,
                score=68.5,
                score_breakdown={
                    "funding_fit": 12.0,
                    "academic_fit": 23.0,
                    "program_relevance": 17.0,
                    "country_preference": 10.0,
                    "deadline_feasibility": 4.0,
                    "evidence_confidence": 2.5,
                },
                overall=OverallEligibility.LIKELY_ELIGIBLE,
                rationale="Top Asian university in Singapore with premier computing faculty.",
                trade_offs=["Tuition support only; living expenses in Singapore must be self-funded."],
                next_actions=["Submit online application before January 15 deadline."],
            ),
        ]
        await opp_repo.save_rankings(job_id, rankings)

        # 6. Emit realistic timeline events
        events_data = [
            (AgentName.COORDINATOR.value, "info", "started", "ScholarPilot multi-agent swarm launched."),
            (AgentName.PROFILE.value, "info", "profile_extracted", "Student profile analyzed: Rahul Sharma (CS, 8.2 CGPA)."),
            (AgentName.PROFILE.value, "info", "github_enriched", "Enriched profile with public GitHub repositories (AI, systems)."),
            (AgentName.SCOUT.value, "info", "candidates_discovered", "Discovered 14 scholarship candidates across Germany, Canada, and Singapore."),
            (AgentName.VERIFY.value, "info", "sources_verified", "Verified 12 candidates against official .edu and .org institutional domains."),
            (AgentName.ELIGIBILITY.value, "info", "criteria_assessed", "Evaluated hard criteria (degree, grade, study field) across candidates."),
            (AgentName.RANKING.value, "success", "ranking_completed", "Ranked Top 5 scholarship opportunities with complete score breakdowns."),
            (AgentName.COORDINATOR.value, "success", "completed", "Evidence-Backed Eligibility Report successfully generated."),
        ]
        for agent, level, event_type, msg in events_data:
            await event_repo.emit_event(job_id, agent=agent, level=level, event_type=event_type, message=msg)

        # 7. Update job status to COMPLETED
        await job_repo.update_status(job_id, JobStatus.COMPLETED)

        print("\n=== Demo Seed Successfully Completed! ===")
        print(f"Profile ID: {profile_id}")
        print(f"Access Token: {access_token}")
        print(f"Job ID: {job_id}")
        print("You can verify this in the API or Frontend right away!")

if __name__ == "__main__":
    asyncio.run(seed_demo())
