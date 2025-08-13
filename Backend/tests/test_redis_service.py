from services.redis_service import RedisService


class FakeRedis:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, expire, value):  # noqa: ARG002
        self.store[key] = value
        return True

    def delete(self, *keys):
        deleted = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                deleted += 1
        return deleted

    def keys(self, pattern):  # naive pattern support: return all
        return list(self.store.keys())


def test_basic_get_set_delete(monkeypatch):
    rs = RedisService()
    # Replace client with fake
    rs.redis_client = FakeRedis()

    assert rs.redis_client.keys("*") == []

    ok = rs.redis_client.setex("k1", 10, "{\"a\":1}")
    assert ok is True
    assert rs.redis_client.get("k1") == '{"a":1}'

    # Through async wrappers
    import asyncio

    async def flow():
        await rs.set("foo", {"x": 1}, 1)
        val = await rs.get("foo")
        assert val == {"x": 1}
        await rs.delete("foo")
        assert await rs.get("foo") is None

    asyncio.get_event_loop().run_until_complete(flow())

