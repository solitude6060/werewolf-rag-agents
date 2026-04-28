from src.rag.corpus import (
    get_rule_corpus,
    get_role_behaviors,
    get_game_rules,
    get_evidence_patterns,
    ALL_CORPUS,
)
from src.rag.retriever import SimpleRetriever, BM25Retriever, get_retriever


def test_get_rule_corpus():
    corpus = get_rule_corpus()
    assert len(corpus) > 0
    assert any("Werewolf" in c for c in corpus)
    assert any("Seer" in c for c in corpus)


def test_role_behaviors_contain_all_roles():
    behaviors = get_role_behaviors()
    role_keywords = ["Werewolf", "Seer", "Medium", "Villager", "Hunter", "Madman"]
    for keyword in role_keywords:
        assert any(keyword in b for b in behaviors), f"Missing role: {keyword}"


def test_simple_retriever_seer():
    retriever = SimpleRetriever()
    results = retriever.retrieve("seer role behavior")
    assert len(results) > 0
    assert any("Seer" in r for r in results)


def test_simple_retriever_werewolf():
    retriever = SimpleRetriever()
    results = retriever.retrieve("werewolf attack")
    assert len(results) > 0
    assert any("werewolf" in r.lower() for r in results)


def test_simple_retriever_vote():
    retriever = SimpleRetriever()
    results = retriever.retrieve("vote for player")
    assert len(results) > 0
    assert any("vote" in r.lower() for r in results)


def test_simple_retriever_default():
    retriever = SimpleRetriever()
    results = retriever.retrieve("random query")
    assert len(results) == 5


def test_bm25_retriever():
    retriever = BM25Retriever()
    results = retriever.retrieve("werewolf seer")
    assert len(results) > 0
    assert any("werewolf" in r.lower() for r in results)


def test_bm25_retriever_no_match():
    retriever = BM25Retriever()
    results = retriever.retrieve("xyz123 no match")
    assert len(results) <= 5


def test_get_context():
    retriever = SimpleRetriever()
    context = retriever.get_context("seer", top_k=3)
    assert len(context) > 0
    assert "- " in context


def test_get_retriever_simple():
    retriever = get_retriever("simple")
    assert isinstance(retriever, SimpleRetriever)


def test_get_retriever_bm25():
    retriever = get_retriever("bm25")
    assert isinstance(retriever, BM25Retriever)


def test_all_corpus_not_empty():
    assert len(ALL_CORPUS) > 0


def test_evidence_patterns():
    patterns = get_evidence_patterns()
    assert len(patterns) > 0
    assert any("Vote" in p for p in patterns)
    assert any("claim" in p.lower() for p in patterns)