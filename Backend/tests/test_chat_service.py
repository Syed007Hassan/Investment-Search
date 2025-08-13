import sys
import types

# Inject a dummy models.company before importing ChatService to avoid DB init side-effects
fake_company = types.ModuleType("models.company")

class CompanyDummy:
    __tablename__ = "Company"

    @staticmethod
    def get_embedding_field():
        return "embedding"

    @staticmethod
    def get_text_search_field():
        return "content"

    def to_dict(self):
        return {"id": 1}

fake_company.Company = CompanyDummy
sys.modules["models.company"] = fake_company

from services.chat import ChatService  # noqa: E402


class FakeSearcher:
    def __init__(self, items):
        self._items = items

    def search_and_embed(self, search_query):  # noqa: ANN001
        return self._items


class DummyCompany:
    def __init__(self, id_, content="", name="N", desc="D", ind="I", size="S", loc="L"):
        self.id = id_
        self.content = content
        self.name = name
        self.description = desc
        self.industry = ind
        self.size = size
        self.location = loc

    def to_str(self):
        return f"Company: {self.name}\nDescription: {self.description}\nIndustry: {self.industry}\nSize: {self.size}\nLocation: {self.location}"


def test_search_companies_basic(monkeypatch):
    cs = ChatService()
    cs.searcher = FakeSearcher([DummyCompany(1, content="A"), DummyCompany(2, content="B")])

    msg, companies = cs.search_companies("query text")
    assert "Retrieved the following companies" in msg
    assert len(companies) == 2


def test_generate_response_with_tool_call_db(monkeypatch):
    cs = ChatService()

    # Make the LLM client return a single tool call once, then a final message
    class FakeChoice:
        def __init__(self, message):
            self.message = message

    class FakeResponse:
        def __init__(self, message):
            self.choices = [FakeChoice(message)]

    class FakeToolCall:
        def __init__(self):
            self.id = "1"
            self.function = type(
                "F", (), {"name": "search_companies", "arguments": '{"search_query": "abc"}'}
            )()

        def model_dump(self):
            return {
                "id": self.id,
                "type": "function",
                "function": {"name": self.function.name, "arguments": self.function.arguments},
            }

    tool_call = FakeToolCall()

    messages = []

    def fake_create(model, messages: list, tool_choice, tools, max_tokens):  # noqa: ANN001
        # first call returns tool call, second returns final content
        if not any(m.get("role") == "tool" for m in messages):
            msg = type("Msg", (), {"tool_calls": [tool_call]})()
        else:
            msg = type("Msg", (), {"tool_calls": None, "content": "final"})()
        return FakeResponse(msg)

    cs.searcher = FakeSearcher([DummyCompany(1, content="A")])
    monkeypatch.setattr(cs.client.chat.completions, "create", fake_create)

    content, companies = cs.generate_response("hello", web_search=False)
    assert content == "final"
    assert len(companies) == 1

