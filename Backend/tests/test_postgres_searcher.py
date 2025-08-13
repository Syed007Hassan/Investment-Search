from types import SimpleNamespace

import pytest

from services.postgres_searcher import PostgresSearcher


class DummyItem:
    def __init__(self, id_):
        self.id = id_


def test_search_and_embed_calls_search_with_vector(monkeypatch):
    ps = PostgresSearcher(db_model=SimpleNamespace(__tablename__="Company", get_embedding_field=lambda: "embedding", get_text_search_field=lambda: "content"))

    # Stub out embedding generation to avoid external calls
    # Patch the Embedding class method used inside PostgresSearcher
    import services.postgres_searcher as ps_mod
    monkeypatch.setattr(
        ps_mod.Embedding,
        "generate_pinecone",
        lambda self, text, dim: [0.5, 0.5, 0.5],
    )

    called = {}

    def fake_search(query_text, query_vector, top, filters):  # noqa: ANN001, ARG001
        called["query_text"] = query_text
        called["query_vector"] = query_vector
        return [DummyItem(1), DummyItem(2)]

    monkeypatch.setattr(PostgresSearcher, "search", staticmethod(fake_search))

    res = ps.search_and_embed(query_text="hello world", top=2)
    assert [item.id for item in res] == [1, 2]
    assert called["query_text"] == "hello world"
    assert isinstance(called["query_vector"], list) and len(called["query_vector"]) > 0


def test_search_and_embed_text_only(monkeypatch):
    ps = PostgresSearcher(db_model=SimpleNamespace(__tablename__="Company", get_embedding_field=lambda: "embedding", get_text_search_field=lambda: "content"))

    # Force vector search disabled path
    def no_embed(*args, **kwargs):  # noqa: ANN001, D401
        raise RuntimeError("should not be called")

    import services.postgres_searcher as ps_mod
    monkeypatch.setattr(ps_mod.Embedding, "generate_pinecone", no_embed)

    def fake_search(query_text, query_vector, top, filters):  # noqa: ANN001, ARG001
        assert query_text == "only text"
        assert query_vector == []
        return [DummyItem(3)]

    monkeypatch.setattr(PostgresSearcher, "search", staticmethod(fake_search))

    res = ps.search_and_embed(query_text="only text", top=1, enable_vector_search=False)
    assert [item.id for item in res] == [3]

