from types import SimpleNamespace

from services.embedding import Embedding


class FakeInference:
    def __init__(self, values_list):
        # values_list: list[list[float]]
        self._values = values_list

    def embed(self, model, inputs, parameters=None):  # noqa: ARG002
        data = [{"values": v} for v in self._values]
        return SimpleNamespace(data=data)


class FakePinecone:
    def __init__(self):
        self.inference = FakeInference([[0.1, 0.2, 0.3]])


def test_generate_pinecone_monkeypatched(monkeypatch):
    def fake_init(self):  # noqa: ANN001
        self.pinecone_client = FakePinecone()
        self.pinecone_model = "fake-model"

    monkeypatch.setattr(Embedding, "__init__", fake_init)
    e = Embedding()

    vec = e.generate_pinecone("hello world")
    assert vec == [0.1, 0.2, 0.3]


def test_generate_multiple_pinecone(monkeypatch):
    def fake_init(self):  # noqa: ANN001
        # two vectors for two inputs
        self.pinecone_client = type("PC", (), {
            "inference": FakeInference([[1.0, 0.0], [0.0, 1.0]])
        })()
        self.pinecone_model = "fake-model"

    monkeypatch.setattr(Embedding, "__init__", fake_init)
    e = Embedding()
    vecs = e.generate_multiple_pinecone(["a", "b"]) 
    assert vecs == [[1.0, 0.0], [0.0, 1.0]]

