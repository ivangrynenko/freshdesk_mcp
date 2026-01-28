import re

import httpx
import pytest

from freshdesk_mcp import server


def _sample_args():
    # Minimal arguments per MCP tool so each call is exercised with mocked HTTP.
    return {
        "get_ticket_fields": (),
        "get_tickets": (1, 2),
        "create_ticket": (
            "Subject",
            "Description",
            "2",
            "1",
            "2",
            "user@example.com",
        ),
        "update_ticket": (123, {"subject": "Updated"}),
        "delete_ticket": (123,),
        "get_ticket": (123,),
        "search_tickets": ("status:2",),
        "get_ticket_conversation": (123,),
        "create_ticket_reply": (123, "Reply body"),
        "create_ticket_note": (123, "Note body"),
        "update_ticket_conversation": (456, "Updated body"),
        "get_agents": (1, 2),
        "list_contacts": (1, 2),
        "get_contact": (123,),
        "search_contacts": ("email:'user@example.com'",),
        "update_contact": (123, {"name": "User"}),
        "list_canned_responses": (123,),
        "list_canned_response_folders": (),
        "view_canned_response": (123,),
        "create_canned_response": ({"title": "Hello", "content": "World"},),
        "update_canned_response": (123, {"title": "Hello2"}),
        "create_canned_response_folder": ("Folder",),
        "update_canned_response_folder": (123, "Folder2"),
        "list_solution_articles": (123,),
        "list_solution_folders": (123,),
        "list_solution_categories": (),
        "view_solution_category": (123,),
        "create_solution_category": ({"name": "Cat"},),
        "update_solution_category": (123, {"name": "Cat2"}),
        "create_solution_category_folder": (123, {"name": "Folder"}),
        "view_solution_category_folder": (123,),
        "update_solution_category_folder": (123, {"name": "Folder2"}),
        "create_solution_article": (123, {"title": "Article", "description": "Body"}),
        "view_solution_article": (123,),
        "update_solution_article": (123, {"title": "Article2"}),
        "view_agent": (123,),
        "create_agent": ({"email": "agent@example.com", "ticket_scope": 1},),
        "update_agent": (123, {"occasional": True}),
        "search_agents": ("email:'agent@example.com'",),
        "list_groups": (1, 2),
        "create_group": ({"name": "Group"},),
        "view_group": (123,),
        "create_ticket_field": ({"label": "X"},),
        "view_ticket_field": (123,),
        "update_ticket_field": (123, {"label": "Y"}),
        "update_group": (123, {"name": "Group2"}),
        "list_contact_fields": (),
        "view_contact_field": (123,),
        "create_contact_field": ({"label": "Phone"},),
        "update_contact_field": (123, {"label": "Phone2"}),
        "get_field_properties": ("status",),
        "list_companies": (1, 2),
        "view_company": (123,),
        "search_companies": ("Acme",),
        "find_company_by_name": ("Acme",),
        "list_company_fields": (),
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("tool_name", sorted(_sample_args().keys()))
async def test_all_mcp_tools_run_offline(httpx_mock, monkeypatch, tool_name):
    monkeypatch.setenv("FRESHDESK_API_KEY", "test_key")
    monkeypatch.setenv("FRESHDESK_DOMAIN", "test-domain.freshdesk.com")

    # Match any Freshdesk API request and return a basic JSON payload.
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "test-domain.freshdesk.com"
        assert request.url.path.startswith("/api/")

        # A few helpers expect structured payloads.
        if request.url.path.endswith("/ticket_fields"):
            return httpx.Response(
                200,
                json=[
                    {"name": "status", "choices": {"Open": 2}},
                    {"name": "priority", "choices": {"Low": 1}},
                ],
            )

        return httpx.Response(200, json={"tool": tool_name, "ok": True})

    httpx_mock.add_callback(
        handler,
        url=re.compile(r"https://test-domain\.freshdesk\.com/api/.*"),
        is_reusable=True,
        is_optional=True,
    )

    fn = getattr(server, tool_name)
    args = _sample_args()[tool_name]

    res = fn(*args)
    if hasattr(res, "__await__"):
        result = await res
    else:
        result = res

    # Ensure a response of some kind came back from the HTTP mock.
    assert result is not None
