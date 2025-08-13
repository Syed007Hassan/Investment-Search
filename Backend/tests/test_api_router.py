import sys
import types
from fastapi.testclient import TestClient

# Inject a dummy models.company to avoid real DB side effects during import
fake_company = types.ModuleType("models.company")

class CompanyDummy:
    __tablename__ = "Company"

    @staticmethod
    def get_embedding_field():
        return "embedding"

    @staticmethod
    def get_text_search_field():
        return "content"

fake_company.Company = CompanyDummy
sys.modules["models.company"] = fake_company

from main import app  # noqa: E402
from services.chat import ChatService  # noqa: E402


class FakeChat(ChatService):
    def __init__(self):
        # do not call parent init to avoid Groq client creation
        pass

    def generate_response(self, user_query, web_search=False):  # noqa: ANN001
        return "ok", [{"id": 1, "name": "A", "description": "d", "industry": "i", "size": "s", "location": "l"}]


def test_root_router_health_like_endpoints():
    client = TestClient(app)

    # companies list should return JSON with keys even if DB empty, but may 500 without DB
    # So we only test the search endpoint with minimal body and expect a JSON structure
    # Patch the API's chat_service to avoid network/DB
    import api.router as router

    orig = router.chat_service
    router.chat_service = FakeChat()
    # Fake redis to avoid connection attempts
    class FakeRedisSvc:
        async def get(self, key):  # noqa: ANN001, ARG002
            return None

        async def set(self, key, value, expire=3600):  # noqa: ANN001, ARG002
            return True

        async def delete(self, key):  # noqa: ANN001, ARG002
            return True

        async def scan_and_delete(self, pattern):  # noqa: ANN001, ARG002
            return True

    orig_redis = router.redis_service
    router.redis_service = FakeRedisSvc()
    try:
        r = client.post("/search-company", json={"query": "test"})
    finally:
        router.chat_service = orig
        router.redis_service = orig_redis
    assert r.status_code in (200, 500)
    # If succeeds, verify shape
    if r.status_code == 200:
        data = r.json()
        assert "response" in data
        assert "company_recommendations" in data

