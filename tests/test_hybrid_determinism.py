from modulehandbook_rag.hybrid_retrieval import _rank_combined_scores


def test_hybrid_score_ties_use_chunk_id_as_stable_tiebreaker():
    scores_a = {"chunk-z": 0.4, "chunk-a": 0.4, "chunk-m": 0.8}
    scores_b = {"chunk-a": 0.4, "chunk-m": 0.8, "chunk-z": 0.4}

    assert _rank_combined_scores(scores_a, 3) == [
        ("chunk-m", 0.8),
        ("chunk-a", 0.4),
        ("chunk-z", 0.4),
    ]
    assert _rank_combined_scores(scores_b, 3) == _rank_combined_scores(scores_a, 3)
