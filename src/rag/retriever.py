"""RAG retriever for game knowledge."""

from typing import Optional
from .corpus import get_rule_corpus


class SimpleRetriever:
    def __init__(self, corpus: Optional[list[str]] = None):
        self.corpus = corpus or get_rule_corpus()

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        query_lower = query.lower()

        if "seer" in query_lower:
            return [c for c in self.corpus if "Seer" in c][:top_k]
        if "werewolf" in query_lower:
            return [c for c in self.corpus if "werewolf" in c.lower()][:top_k]
        if "medium" in query_lower:
            return [c for c in self.corpus if "Medium" in c][:top_k]
        if "hunter" in query_lower:
            return [c for c in self.corpus if "Hunter" in c][:top_k]
        if "madman" in query_lower:
            return [c for c in self.corpus if "Madman" in c][:top_k]
        if "vote" in query_lower or "accusation" in query_lower:
            return [c for c in self.corpus if "Vote" in c or "vote" in c.lower()][:top_k]
        if "death" in query_lower:
            return [c for c in self.corpus if "death" in c.lower()][:top_k]
        if "claim" in query_lower:
            return [c for c in self.corpus if "claim" in c.lower()][:top_k]

        return self.corpus[:top_k]

    def get_context(self, query: str, top_k: int = 5) -> str:
        retrieved = self.retrieve(query, top_k)
        return "\n".join(f"- {item}" for item in retrieved)


class BM25Retriever:
    def __init__(self, corpus: Optional[list[str]] = None):
        self.corpus = corpus or get_rule_corpus()

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        query_terms = query.lower().split()

        scored = []
        for item in self.corpus:
            item_lower = item.lower()
            score = sum(1 for term in query_terms if term in item_lower)
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    def get_context(self, query: str, top_k: int = 5) -> str:
        retrieved = self.retrieve(query, top_k)
        return "\n".join(f"- {item}" for item in retrieved)


def get_retriever(retriever_type: str = "simple") -> SimpleRetriever | BM25Retriever:
    if retriever_type == "bm25":
        return BM25Retriever()
    return SimpleRetriever()