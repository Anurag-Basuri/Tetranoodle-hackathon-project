from datetime import date
from typing import List, Dict, Tuple, Optional
from app.domain.enums import FundingType, CriterionKind, CriterionStatus, OverallEligibility
from app.domain.profile import StudentProfile
from app.domain.opportunity import Opportunity, RankedOpportunity
from app.domain.evidence import CriterionAssessment

def score_funding_fit(opportunity: Opportunity, profile: StudentProfile) -> float:
    # Score based on financial support level
    weights = {
        FundingType.FULL: 25.0,
        FundingType.PARTIAL: 15.0,
        FundingType.TUITION_ONLY: 12.0,
        FundingType.UNSPECIFIED: 5.0,
        FundingType.NONE: 0.0,
    }
    score = weights.get(opportunity.funding_type, 5.0)
    # Halve funding weight if applicant has no financial need
    if not profile.needs_funding:
        score = score / 2.0
    return round(score, 1)

def score_academic_fit(assessments: List[CriterionAssessment], criteria_by_id: Dict[str, CriterionKind]) -> float:
    # Score based on degree, grade, and field assessments
    academic_kinds = {CriterionKind.DEGREE_LEVEL, CriterionKind.MIN_GRADE, CriterionKind.FIELD_OF_STUDY}
    academic_assessments = [
        a for a in assessments
        if criteria_by_id.get(a.criterion_id) in academic_kinds
    ]
    if not academic_assessments:
        return 15.0

    points = 0.0
    for a in academic_assessments:
        if a.status == CriterionStatus.MEETS:
            points += 1.0
        elif a.status == CriterionStatus.LIKELY_MEETS:
            points += 0.7
        elif a.status in (CriterionStatus.UNKNOWN, CriterionStatus.NEEDS_REVIEW):
            points += 0.3
        else:
            points += 0.0

    score = (points / len(academic_assessments)) * 25.0
    return round(score, 1)

def score_country_preference(opportunity: Opportunity, profile: StudentProfile) -> float:
    # Reward opportunities in student's target destinations
    if not profile.target_countries:
        return 4.0
    if not opportunity.country:
        return 2.0

    opp_country = opportunity.country.strip().lower()
    for tc in profile.target_countries:
        if tc.strip().lower() in opp_country or opp_country in tc.strip().lower():
            return 10.0
    return 0.0

def score_deadline_feasibility(opportunity: Opportunity, today: Optional[date] = None) -> float:
    # Score how manageable the application timeline is
    today = today or date.today()
    if not opportunity.deadline:
        return 0.0

    days_left = (opportunity.deadline - today).days
    if days_left > 60:
        return 10.0
    elif days_left >= 30:
        return 7.0
    elif days_left >= 14:
        return 4.0
    elif days_left > 0:
        return 1.0
    return 0.0

def score_evidence_confidence(opportunity: Opportunity) -> float:
    # Ratio of verified quotes for hard criteria
    hard_criteria = [c for c in opportunity.criteria if c.is_hard]
    if not hard_criteria:
        return 5.0

    verified_count = sum(
        1 for c in hard_criteria
        if c.evidence and c.evidence.quote_verified
    )
    score = (verified_count / len(hard_criteria)) * 10.0
    return round(score, 1)

def compute_opportunity_score(
    opportunity: Opportunity,
    assessments: List[CriterionAssessment],
    profile: StudentProfile,
    relevance_score: float = 0.75,
    today: Optional[date] = None,
) -> Tuple[float, Dict[str, float]]:
    # Combine the 6 scoring dimensions
    criteria_map = {c.id: c.kind for c in opportunity.criteria}

    funding = score_funding_fit(opportunity, profile)
    academic = score_academic_fit(assessments, criteria_map)
    relevance = round(max(0.0, min(1.0, relevance_score)) * 20.0, 1)
    country = score_country_preference(opportunity, profile)
    deadline = score_deadline_feasibility(opportunity, today)
    confidence = score_evidence_confidence(opportunity)

    total = round(funding + academic + relevance + country + deadline + confidence, 1)
    breakdown = {
        "funding": funding,
        "academic": academic,
        "relevance": relevance,
        "country": country,
        "deadline": deadline,
        "evidence": confidence,
    }
    return total, breakdown

def rank_opportunities(
    opportunities: List[Opportunity],
    assessments_by_opp: Dict[str, List[CriterionAssessment]],
    overall_by_opp: Dict[str, OverallEligibility],
    profile: StudentProfile,
    relevance_scores: Optional[Dict[str, float]] = None,
    today: Optional[date] = None,
) -> List[RankedOpportunity]:
    # Filter out ineligible programs, score, cap at 2 per institution, select top 5
    today = today or date.today()
    relevance_scores = relevance_scores or {}

    scored_list = []
    for opp in opportunities:
        opp_id_str = str(opp.id)
        overall = overall_by_opp.get(opp_id_str, OverallEligibility.NEEDS_INFO)
        if overall == OverallEligibility.NOT_ELIGIBLE:
            continue

        assessments = assessments_by_opp.get(opp_id_str, [])
        rel = relevance_scores.get(opp_id_str, 0.75)
        score, breakdown = compute_opportunity_score(opp, assessments, profile, rel, today)

        # Build straightforward explanation from criteria assessment
        met_count = sum(1 for a in assessments if a.status == CriterionStatus.MEETS)
        rationale = f"Strong fit ({score}/100) with {met_count} verified criteria met and {opp.funding_type.value} funding."

        trade_offs = []
        if opp.funding_type in (FundingType.PARTIAL, FundingType.TUITION_ONLY):
            trade_offs.append(f"Provides {opp.funding_type.value} funding; additional living expenses needed.")
        if breakdown["deadline"] <= 4.0 and opp.deadline:
            trade_offs.append("Application deadline is approaching soon.")

        actions = [a.next_action for a in assessments if a.next_action]

        ranked_item = RankedOpportunity(
            opportunity_id=opp.id,
            rank=None,
            score=score,
            score_breakdown=breakdown,
            overall=overall,
            rationale=rationale,
            trade_offs=trade_offs,
            next_actions=actions[:3],
        )
        scored_list.append((opp, ranked_item))

    # Sort descending by score
    scored_list.sort(key=lambda pair: pair[1].score, reverse=True)

    # Diversity limit: at most 2 opportunities per institution
    institution_counts: Dict[str, int] = {}
    top_ranked: List[RankedOpportunity] = []
    current_rank = 1

    for opp, ranked_item in scored_list:
        inst_key = (opp.institution or "general").strip().lower()
        if institution_counts.get(inst_key, 0) >= 2:
            continue

        institution_counts[inst_key] = institution_counts.get(inst_key, 0) + 1
        ranked_item.rank = current_rank
        top_ranked.append(ranked_item)
        current_rank += 1

        if len(top_ranked) == 5:
            break

    return top_ranked
