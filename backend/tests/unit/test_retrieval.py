from app.tools.retrieval import chunk_text, select_chunks

def test_chunk_text_overlap():
    text = "A" * 1500
    chunks = chunk_text(text, chunk_size=800, chunk_overlap=150)
    assert len(chunks) >= 2
    assert len(chunks[0]) == 800

def test_select_chunks_bm25_relevance():
    # Chunks with scholarship eligibility keywords must be ranked higher
    chunk_irrelevant = "This section discusses the history of the university campus founded in 1890 with brick buildings."
    chunk_relevant = "International scholarship eligibility: applicants must have minimum 8.0 CGPA and IELTS 7.5. Full tuition funding provided."
    chunk_filler = "The cafeteria offers daily meals for enrolled students including vegetarian options."

    full_text = f"{chunk_irrelevant}\n\n{chunk_relevant}\n\n{chunk_filler}"
    selected = select_chunks(full_text, query_terms=["eligibility", "scholarship", "gpa", "ielts"], max_tokens=1000)

    # Top selected chunk must contain the eligibility details
    assert len(selected) > 0
    assert "eligibility" in selected[0].lower()
