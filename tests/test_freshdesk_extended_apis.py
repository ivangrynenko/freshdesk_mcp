import pytest
import asyncio
import os
from httpx import Response, Request
from typing import Dict, Any, List, Optional, Union

# Mock server functions by importing the server module
from src.freshdesk_mcp import server

# Dummy values for environment variables
TEST_API_KEY = "test_api_key"
TEST_DOMAIN = "test-domain.freshdesk.com"
BASE_URL = f"https://{TEST_DOMAIN}/api/v2"

# Common error responses
ERROR_RESPONSES = [
    (400, {"description": "Bad Request", "errors": [{"field": "name", "message": "Missing required value", "code": "missing_field"}]}),
    (401, {"description": "Unauthorized", "errors": []}),
    (403, {"description": "Forbidden", "errors": []}),
    (404, {"description": "Resource not found", "errors": []}),
    (500, {"description": "Internal Server Error", "errors": []}),
]

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("FRESHDESK_API_KEY", TEST_API_KEY)
    monkeypatch.setenv("FRESHDESK_DOMAIN", TEST_DOMAIN)

class TestContactFunctions:
    CONTACT_ID = 123
    SAMPLE_CONTACT_PAYLOAD = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "mobile": "0987654321",
    }
    CREATED_CONTACT_RESPONSE = {**SAMPLE_CONTACT_PAYLOAD, "id": CONTACT_ID, "active": True}

    @pytest.mark.asyncio
    async def test_create_contact_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts",
            method="POST",
            json=self.CREATED_CONTACT_RESPONSE,
            status_code=201,
            match_json=self.SAMPLE_CONTACT_PAYLOAD  # Ensure payload is sent correctly
        )
        result = await server.create_contact(self.SAMPLE_CONTACT_PAYLOAD)
        assert result == self.CREATED_CONTACT_RESPONSE

    @pytest.mark.asyncio
    async def test_create_contact_success_with_avatar(self, httpx_mock, tmp_path):
        avatar_file = tmp_path / "avatar.png"
        avatar_file.write_text("dummy_image_content")
        
        payload_with_avatar_path = {**self.SAMPLE_CONTACT_PAYLOAD, "avatar": str(avatar_file)}
        
        # httpx_mock needs to match multipart/form-data
        # We can't easily match_content for multipart with pytest-httpx directly in add_response
        # So we'll check the request object in a callback if precise matching is needed
        # For now, just ensure it calls the right URL and method.
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts",
            method="POST",
            json=self.CREATED_CONTACT_RESPONSE,
            status_code=201
        )
        
        result = await server.create_contact(payload_with_avatar_path)
        assert result == self.CREATED_CONTACT_RESPONSE
        
        # Verify the request was multipart (basic check)
        request = httpx_mock.get_request()
        assert request is not None
        assert "multipart/form-data" in request.headers.get("Content-Type", "")


    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_create_contact_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts",
            method="POST",
            json=error_json,
            status_code=status_code
        )
        result = await server.create_contact(self.SAMPLE_CONTACT_PAYLOAD)
        assert "error" in result
        assert f"Failed to create contact" in result["error"]

    @pytest.mark.asyncio
    async def test_delete_contact_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}",
            method="DELETE",
            status_code=204
        )
        result = await server.delete_contact(self.CONTACT_ID)
        assert result == {"success": True, "message": f"Contact {self.CONTACT_ID} deleted successfully."}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_delete_contact_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}",
            method="DELETE",
            json=error_json,
            status_code=status_code
        )
        result = await server.delete_contact(self.CONTACT_ID)
        assert "error" in result
        assert f"Failed to delete contact {self.CONTACT_ID}" in result["error"]

    @pytest.mark.asyncio
    async def test_hard_delete_contact_success_no_force(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/hard_delete", # No ?force=true
            method="DELETE",
            status_code=204
        )
        result = await server.hard_delete_contact(self.CONTACT_ID, force=False)
        assert result == {"success": True, "message": f"Contact {self.CONTACT_ID} hard deleted successfully."}
        request = httpx_mock.get_request()
        assert request is not None
        assert "force=true" not in str(request.url)


    @pytest.mark.asyncio
    async def test_hard_delete_contact_success_with_force(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/hard_delete?force=true",
            method="DELETE",
            status_code=204
        )
        result = await server.hard_delete_contact(self.CONTACT_ID, force=True)
        assert result == {"success": True, "message": f"Contact {self.CONTACT_ID} hard deleted successfully."}
        request = httpx_mock.get_request()
        assert request is not None
        assert "force=true" in str(request.url)


    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_hard_delete_contact_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/hard_delete", # Omitting force for general error tests
            method="DELETE",
            json=error_json,
            status_code=status_code
        )
        result = await server.hard_delete_contact(self.CONTACT_ID)
        assert "error" in result
        assert f"Failed to hard delete contact {self.CONTACT_ID}" in result["error"]

    MAKE_AGENT_PAYLOAD = {"ticket_scope": 1, "group_ids": [101]} # Example: Global Access
    MADE_AGENT_RESPONSE = {"id": CONTACT_ID, "available": True, "occasional": False, "contact": {"id": CONTACT_ID, "name": "Test User"}}

    @pytest.mark.asyncio
    async def test_make_agent_from_contact_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/make_agent",
            method="PUT",
            json=self.MADE_AGENT_RESPONSE,
            status_code=200, # API usually returns 200 for this
            match_json=self.MAKE_AGENT_PAYLOAD
        )
        result = await server.make_agent_from_contact(self.CONTACT_ID, self.MAKE_AGENT_PAYLOAD)
        assert result == self.MADE_AGENT_RESPONSE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_make_agent_from_contact_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/make_agent",
            method="PUT",
            json=error_json,
            status_code=status_code
        )
        result = await server.make_agent_from_contact(self.CONTACT_ID, self.MAKE_AGENT_PAYLOAD)
        assert "error" in result
        assert f"Failed to make agent from contact {self.CONTACT_ID}" in result["error"]

    @pytest.mark.asyncio
    async def test_restore_contact_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/restore",
            method="PUT",
            status_code=204
        )
        result = await server.restore_contact(self.CONTACT_ID)
        assert result == {"success": True, "message": f"Contact {self.CONTACT_ID} restored successfully."}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_restore_contact_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/restore",
            method="PUT",
            json=error_json, # Some APIs might not return body for PUT on error, but good to test
            status_code=status_code
        )
        result = await server.restore_contact(self.CONTACT_ID)
        assert "error" in result
        assert f"Failed to restore contact {self.CONTACT_ID}" in result["error"]

    @pytest.mark.asyncio
    async def test_send_invite_to_contact_success_204(self, httpx_mock): # API doc says 200, but often 204
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/send_invite",
            method="PUT",
            status_code=204
        )
        result = await server.send_invite_to_contact(self.CONTACT_ID)
        assert result == {"success": True, "message": f"Invitation sent to contact {self.CONTACT_ID} successfully."}

    @pytest.mark.asyncio
    async def test_send_invite_to_contact_success_200(self, httpx_mock):
        mock_response_body = {"message": "Invitation sent"}
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/send_invite",
            method="PUT",
            status_code=200,
            json=mock_response_body
        )
        result = await server.send_invite_to_contact(self.CONTACT_ID)
        assert result == {"success": True, "message": f"Invitation sent to contact {self.CONTACT_ID} successfully.", "details": mock_response_body}


    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_send_invite_to_contact_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contacts/{self.CONTACT_ID}/send_invite",
            method="PUT",
            json=error_json,
            status_code=status_code
        )
        result = await server.send_invite_to_contact(self.CONTACT_ID)
        assert "error" in result
        assert f"Failed to send invite to contact {self.CONTACT_ID}" in result["error"]


class TestCompanyFunctions:
    COMPANY_ID = 789
    SAMPLE_COMPANY_PAYLOAD = {"name": "Test Company Inc.", "domains": ["testcompany.com"]}
    CREATED_COMPANY_RESPONSE = {**SAMPLE_COMPANY_PAYLOAD, "id": COMPANY_ID}

    @pytest.mark.asyncio
    async def test_create_company_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/companies",
            method="POST",
            json=self.CREATED_COMPANY_RESPONSE,
            status_code=201,
            match_json=self.SAMPLE_COMPANY_PAYLOAD
        )
        result = await server.create_company(self.SAMPLE_COMPANY_PAYLOAD)
        assert result == self.CREATED_COMPANY_RESPONSE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_create_company_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/companies",
            method="POST",
            json=error_json,
            status_code=status_code
        )
        result = await server.create_company(self.SAMPLE_COMPANY_PAYLOAD)
        assert "error" in result
        assert "Failed to create company" in result["error"]

    @pytest.mark.asyncio
    async def test_delete_company_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/companies/{self.COMPANY_ID}",
            method="DELETE",
            status_code=204
        )
        result = await server.delete_company(self.COMPANY_ID)
        assert result == {"success": True, "message": f"Company {self.COMPANY_ID} deleted successfully."}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_delete_company_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/companies/{self.COMPANY_ID}",
            method="DELETE",
            json=error_json,
            status_code=status_code
        )
        result = await server.delete_company(self.COMPANY_ID)
        assert "error" in result
        assert f"Failed to delete company {self.COMPANY_ID}" in result["error"]


class TestTicketFieldFunctions:
    TICKET_FIELD_ID = 456

    @pytest.mark.asyncio
    async def test_delete_ticket_field_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/admin/ticket_fields/{self.TICKET_FIELD_ID}",
            method="DELETE",
            status_code=204
        )
        result = await server.delete_ticket_field(self.TICKET_FIELD_ID)
        assert result == {"message": f"Ticket field {self.TICKET_FIELD_ID} deleted successfully"}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_delete_ticket_field_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/admin/ticket_fields/{self.TICKET_FIELD_ID}",
            method="DELETE",
            json=error_json,
            status_code=status_code
        )
        result = await server.delete_ticket_field(self.TICKET_FIELD_ID)
        assert "error" in result
        assert f"Failed to delete ticket field {self.TICKET_FIELD_ID}" in result["error"]


class TestContactFieldFunctions:
    CONTACT_FIELD_ID = 789

    @pytest.mark.asyncio
    async def test_delete_contact_field_success(self, httpx_mock):
        httpx_mock.add_response(
            # Note: API path is singular 'contact_field' for delete by ID
            url=f"{BASE_URL}/contact_field/{self.CONTACT_FIELD_ID}",
            method="DELETE",
            status_code=204
        )
        result = await server.delete_contact_field(self.CONTACT_FIELD_ID)
        assert result == {"message": f"Contact field {self.CONTACT_FIELD_ID} deleted successfully"}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_delete_contact_field_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/contact_field/{self.CONTACT_FIELD_ID}",
            method="DELETE",
            json=error_json,
            status_code=status_code
        )
        result = await server.delete_contact_field(self.CONTACT_FIELD_ID)
        assert "error" in result
        assert f"Failed to delete contact field {self.CONTACT_FIELD_ID}" in result["error"]


class TestCompanyFieldFunctions:
    COMPANY_FIELD_ID = 101
    SAMPLE_COMPANY_FIELD_PAYLOAD = {"label": "Industry Type", "type": "custom_dropdown", "choices": [{"value": "Tech"}, {"value":"Finance"}]}
    CREATED_COMPANY_FIELD_RESPONSE = {**SAMPLE_COMPANY_FIELD_PAYLOAD, "id": COMPANY_FIELD_ID, "name": "cf_industry_type"} # name is auto-generated
    UPDATED_COMPANY_FIELD_PAYLOAD = {"label": "Industry Vertical"}
    UPDATED_COMPANY_FIELD_RESPONSE = {**CREATED_COMPANY_FIELD_RESPONSE, **UPDATED_COMPANY_FIELD_PAYLOAD}


    @pytest.mark.asyncio
    async def test_create_company_field_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/company_fields",
            method="POST",
            json=self.CREATED_COMPANY_FIELD_RESPONSE,
            status_code=201,
            match_json=self.SAMPLE_COMPANY_FIELD_PAYLOAD
        )
        result = await server.create_company_field(self.SAMPLE_COMPANY_FIELD_PAYLOAD)
        assert result == self.CREATED_COMPANY_FIELD_RESPONSE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_create_company_field_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/company_fields",
            method="POST",
            json=error_json,
            status_code=status_code
        )
        result = await server.create_company_field(self.SAMPLE_COMPANY_FIELD_PAYLOAD)
        assert "error" in result
        assert "Failed to create company field" in result["error"]

    @pytest.mark.asyncio
    async def test_view_company_field_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/company_fields/{self.COMPANY_FIELD_ID}",
            method="GET",
            json=self.CREATED_COMPANY_FIELD_RESPONSE,
            status_code=200
        )
        result = await server.view_company_field(self.COMPANY_FIELD_ID)
        assert result == self.CREATED_COMPANY_FIELD_RESPONSE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_view_company_field_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/company_fields/{self.COMPANY_FIELD_ID}",
            method="GET",
            json=error_json,
            status_code=status_code
        )
        result = await server.view_company_field(self.COMPANY_FIELD_ID)
        assert "error" in result
        assert f"Failed to view company field {self.COMPANY_FIELD_ID}" in result["error"]

    @pytest.mark.asyncio
    async def test_update_company_field_success(self, httpx_mock):
        httpx_mock.add_response(
            # Note: API path is singular 'company_field' for update by ID
            url=f"{BASE_URL}/company_field/{self.COMPANY_FIELD_ID}",
            method="PUT",
            json=self.UPDATED_COMPANY_FIELD_RESPONSE,
            status_code=200,
            match_json=self.UPDATED_COMPANY_FIELD_PAYLOAD
        )
        result = await server.update_company_field(self.COMPANY_FIELD_ID, self.UPDATED_COMPANY_FIELD_PAYLOAD)
        assert result == self.UPDATED_COMPANY_FIELD_RESPONSE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_update_company_field_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/company_field/{self.COMPANY_FIELD_ID}",
            method="PUT",
            json=error_json,
            status_code=status_code
        )
        result = await server.update_company_field(self.COMPANY_FIELD_ID, self.UPDATED_COMPANY_FIELD_PAYLOAD)
        assert "error" in result
        assert f"Failed to update company field {self.COMPANY_FIELD_ID}" in result["error"]

    @pytest.mark.asyncio
    async def test_delete_company_field_success(self, httpx_mock):
        httpx_mock.add_response(
            # Note: API path is singular 'company_field' for delete by ID
            url=f"{BASE_URL}/company_field/{self.COMPANY_FIELD_ID}",
            method="DELETE",
            status_code=204
        )
        result = await server.delete_company_field(self.COMPANY_FIELD_ID)
        assert result == {"success": True, "message": f"Company field {self.COMPANY_FIELD_ID} deleted successfully."}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_delete_company_field_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/company_field/{self.COMPANY_FIELD_ID}",
            method="DELETE",
            json=error_json,
            status_code=status_code
        )
        result = await server.delete_company_field(self.COMPANY_FIELD_ID)
        assert "error" in result
        assert f"Failed to delete company field {self.COMPANY_FIELD_ID}" in result["error"]


class TestAgentFunctions:
    AGENT_ID = 202
    CURRENT_AGENT_RESPONSE = {"id": AGENT_ID, "email": "agent@example.com", "type": "support_agent"}

    @pytest.mark.asyncio
    async def test_delete_agent_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/agents/{self.AGENT_ID}",
            method="DELETE",
            status_code=204
        )
        result = await server.delete_agent(self.AGENT_ID)
        assert result == {"message": f"Agent {self.AGENT_ID} deleted successfully and downgraded to contact."}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_delete_agent_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/agents/{self.AGENT_ID}",
            method="DELETE",
            json=error_json,
            status_code=status_code
        )
        result = await server.delete_agent(self.AGENT_ID)
        assert "error" in result
        assert f"Failed to delete agent {self.AGENT_ID}" in result["error"]

    @pytest.mark.asyncio
    async def test_get_current_agent_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/agents/me",
            method="GET",
            json=self.CURRENT_AGENT_RESPONSE,
            status_code=200
        )
        result = await server.get_current_agent()
        assert result == self.CURRENT_AGENT_RESPONSE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_get_current_agent_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/agents/me",
            method="GET",
            json=error_json,
            status_code=status_code
        )
        result = await server.get_current_agent()
        assert "error" in result
        assert "Failed to get current agent" in result["error"]


class TestRoleFunctions:
    ROLE_ID = 303
    ROLE_RESPONSE = {"id": ROLE_ID, "name": "Support Manager", "description": "Manages support team"}
    LIST_ROLES_RESPONSE = {"roles": [ROLE_RESPONSE, {"id": 304, "name": "Support Agent"}]} # API returns dict with 'roles' key

    @pytest.mark.asyncio
    async def test_view_role_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/roles/{self.ROLE_ID}",
            method="GET",
            json=self.ROLE_RESPONSE,
            status_code=200
        )
        result = await server.view_role(self.ROLE_ID)
        assert result == self.ROLE_RESPONSE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_view_role_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/roles/{self.ROLE_ID}",
            method="GET",
            json=error_json,
            status_code=status_code
        )
        result = await server.view_role(self.ROLE_ID)
        assert "error" in result
        assert f"Failed to view role {self.ROLE_ID}" in result["error"]

    @pytest.mark.asyncio
    async def test_list_roles_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/roles",
            method="GET",
            json=self.LIST_ROLES_RESPONSE, # Mocking the structure Freshdesk provides
            status_code=200
        )
        result = await server.list_roles()
        assert result == self.LIST_ROLES_RESPONSE # Expecting the dict with 'roles' key

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_list_roles_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/roles",
            method="GET",
            json=error_json,
            status_code=status_code
        )
        result = await server.list_roles()
        assert "error" in result
        assert "Failed to list roles" in result["error"]


class TestProductFunctions:
    PRODUCT_ID = 4040
    PRODUCT_RESPONSE = {"id": PRODUCT_ID, "name": "Awesome Product", "description": "The best product ever."}
    # Freshdesk list products API returns a list directly
    LIST_PRODUCTS_RESPONSE = [PRODUCT_RESPONSE, {"id": 4041, "name": "Another Product"}]


    @pytest.mark.asyncio
    async def test_view_product_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/products/{self.PRODUCT_ID}",
            method="GET",
            json=self.PRODUCT_RESPONSE,
            status_code=200
        )
        result = await server.view_product(self.PRODUCT_ID)
        assert result == self.PRODUCT_RESPONSE

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_view_product_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/products/{self.PRODUCT_ID}",
            method="GET",
            json=error_json,
            status_code=status_code
        )
        result = await server.view_product(self.PRODUCT_ID)
        assert "error" in result
        assert f"Failed to view product {self.PRODUCT_ID}" in result["error"]

    @pytest.mark.asyncio
    async def test_list_products_success(self, httpx_mock):
        httpx_mock.add_response(
            url=f"{BASE_URL}/products",
            method="GET",
            json=self.LIST_PRODUCTS_RESPONSE, # Returns a list directly
            status_code=200
        )
        result = await server.list_products()
        assert result == self.LIST_PRODUCTS_RESPONSE # Expecting the list directly

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code, error_json", ERROR_RESPONSES)
    async def test_list_products_errors(self, httpx_mock, status_code, error_json):
        httpx_mock.add_response(
            url=f"{BASE_URL}/products",
            method="GET",
            json=error_json,
            status_code=status_code
        )
        result = await server.list_products()
        assert "error" in result
        assert "Failed to list products" in result["error"]

# Example of how to test specific Pydantic validation errors if needed
# This would require more specific error responses from the server-side code
# or testing the Pydantic models directly.
# For now, the generic error handling for 400 from API is covered.

# Placeholder for tests requiring file uploads (e.g. create_contact with avatar)
# These might need more specific setup for multipart/form-data if match_content is required.
# The current create_contact_success_with_avatar is a basic check.
# More advanced multipart matching:
# from httpx_toolbelt import MultipartDecoder
# def callback(request: Request):
#     decoder = MultipartDecoder(request.content, request.headers['Content-Type'])
#     # ... inspect decoder.parts ...
#     return Response(201, json=...)
# httpx_mock.add_callback(callback, url=..., method="POST")
# However, this is more involved and might be overkill unless strict payload matching is essential.
# The current `match_json` for JSON payloads is sufficient for most create/update tests.
# For multipart, checking the Content-Type header and that the server can process it is a good start.
