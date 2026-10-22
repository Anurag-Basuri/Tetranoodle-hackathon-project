import re
from typing import List, Optional
from rank_bm25 import BM25Okapi

DEFAULT_QUERY_TERMS = [
    "eligibility",
    "requirements",
    "deadline",
    "funding",
    "tuition",
    "scholarship",
    "language",
    "ielts",
    "gpa",
    "international",
    "admission",
    "application",
]

def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> List[str]:
    # Split text into overlapping windows
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

def tokenize_words(text: str) -> List[str]:
    # Simple whitespace and punctuation tokenizer
    return re.findall(r"\w+", text.lower())

def select_chunks(
    text: str,
    query_terms: Optional[List[str]] = None,
    max_tokens: int = 6000,
    chunk_size: int = 800,
) -> List[str]:
    # Select most relevant chunks using BM25 ranking
    if not text:
        return []

    chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=150)
    if len(chunks) <= 3:
        return chunks

    terms = query_terms or DEFAULT_QUERY_TERMS
    tokenized_query = tokenize_words(" ".join(terms))

    tokenized_corpus = [tokenize_words(c) for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    scores = bm25.get_scores(tokenized_query)
    scored_chunks = list(zip(chunks, scores))

    # Sort descending by BM25 relevance score
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    selected = []
    current_chars = 0
    max_chars = max_tokens * 4

    for chunk, score in scored_chunks:
        if current_chars + len(chunk) > max_chars:
            break
        selected.append(chunk)
        current_chars += len(chunk)

    return selected or chunks[:3]
