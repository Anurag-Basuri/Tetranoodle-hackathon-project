import pytest
from app.domain.enums import DegreeLevel
from app.domain.profile import StudentProfile, Grade
from app.agents.graph import build_research_graph, fan_out_candidates

def make_profile():
    return StudentProfile(
        full_name="Rahul Sharma",
        nationality="India",
        degree_level_held=DegreeLevel.BACHELOR,
        degree_level_target=DegreeLevel.MASTER,
        field_of_study="Computer Science",
        grade=Grade(value=8.2, scale=10.0),
        target_countries=["Germany"],
    )

def test_graph_compilation():
    # Verify graph compiles without topology or node errors
    graph = build_research_graph()
    assert graph is not None

def test_fan_out_logic():
    # Verify candidate list fans out to Send objects
    from app.domain.opportunity import Candidate
    profile = make_profile()
    c1 = Candidate(name="TUM Master", url="https://tum.de/program")
    c2 = Candidate(name="Waterloo CS", url="https://uwaterloo.ca/cs")

    state = {
        "job_id": "test-job-123",
        "profile_input": profile,
        "profile": profile,
        "candidates": [c1, c2],
    }

    sends = fan_out_candidates(state)
    assert len(sends) == 2
    assert sends[0].node == "candidate_pipeline"
    assert sends[0].arg["candidate"].name == "TUM Master"
