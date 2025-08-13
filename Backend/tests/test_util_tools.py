from util.tool import get_all_tools


def test_get_all_tools_web_enabled():
    tools = get_all_tools(web_search_enabled=True)
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "web_search_companies"


def test_get_all_tools_db_only():
    tools = get_all_tools(web_search_enabled=False)
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "search_companies"

