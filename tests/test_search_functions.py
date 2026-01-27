import pytest

from freshdesk_mcp.server import build_complex_search_query, build_search_query, search_tickets


def test_build_search_query_string():
    assert build_search_query("type", "Question") == "type:'Question'"


def test_build_search_query_numeric_and_null_and_bool():
    assert build_search_query("status", 2) == "status:2"
    assert build_search_query("status", None) == "status:null"
    assert build_search_query("spam", True) == "spam:true"
    assert build_search_query("spam", False) == "spam:false"


def test_build_search_query_comparison_operator():
    assert build_search_query("created_at", "2023-01-01", ">") == "created_at:>'2023-01-01'"
    assert build_search_query("priority", 2, ">=") == "priority:>2"
    assert build_search_query("priority", 2, "<=") == "priority:<2"


def test_build_complex_search_query():
    q1 = build_search_query("status", 2)
    q2 = build_search_query("priority", 3)
    assert build_complex_search_query(q1, q2, operator="AND") == "(status:2 AND priority:3)"


@pytest.mark.asyncio
async def test_search_tickets_free_text_is_converted_and_quoted(httpx_mock, monkeypatch):
    monkeypatch.setenv("FRESHDESK_API_KEY", "test_key")
    monkeypatch.setenv("FRESHDESK_DOMAIN", "test-domain.freshdesk.com")

    expected_query = '"(description:\'payment issue\' OR subject:\'payment issue\')"'

    httpx_mock.add_response(
        method="GET",
        url="https://test-domain.freshdesk.com/api/v2/search/tickets",
        match_params={"query": expected_query},
        json={"results": []},
        status_code=200,
    )

    await search_tickets("payment issue")

    req = httpx_mock.get_request()
    assert req is not None
    assert req.url.params.get("query") == expected_query


@pytest.mark.asyncio
async def test_search_tickets_preserves_structured_query_and_outer_quotes(httpx_mock, monkeypatch):
    monkeypatch.setenv("FRESHDESK_API_KEY", "test_key")
    monkeypatch.setenv("FRESHDESK_DOMAIN", "test-domain.freshdesk.com")

    expected_query = '"status:2 AND priority:3"'

    httpx_mock.add_response(
        method="GET",
        url="https://test-domain.freshdesk.com/api/v2/search/tickets",
        match_params={"query": expected_query},
        json={"results": []},
        status_code=200,
    )

    await search_tickets("status:2 AND priority:3")

    req = httpx_mock.get_request()
    assert req is not None
    assert req.url.params.get("query") == expected_query
