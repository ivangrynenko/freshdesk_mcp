import httpx
from mcp.server.fastmcp import FastMCP
import logging
import os
import base64
from typing import Optional, Dict, Union, Any, List
from enum import IntEnum, Enum
import re
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize FastMCP server
mcp = FastMCP("freshdesk-mcp")

FRESHDESK_API_KEY = os.getenv("FRESHDESK_API_KEY")
FRESHDESK_DOMAIN = os.getenv("FRESHDESK_DOMAIN")


def parse_link_header(link_header: str) -> Dict[str, Optional[int]]:
    """Parse the Link header to extract pagination information.

    Args:
        link_header: The Link header string from the response

    Returns:
        Dictionary containing next and prev page numbers
    """
    pagination = {
        "next": None,
        "prev": None
    }

    if not link_header:
        return pagination

    # Split multiple links if present
    links = link_header.split(',')

    for link in links:
        # Extract URL and rel
        match = re.search(r'<(.+?)>;\s*rel="(.+?)"', link)
        if match:
            url, rel = match.groups()
            # Extract page number from URL
            page_match = re.search(r'page=(\d+)', url)
            if page_match:
                page_num = int(page_match.group(1))
                pagination[rel] = page_num

    return pagination

# enums of ticket properties
class TicketSource(IntEnum):
    EMAIL = 1
    PORTAL = 2
    PHONE = 3
    CHAT = 7
    FEEDBACK_WIDGET = 9
    OUTBOUND_EMAIL = 10

class TicketStatus(IntEnum):
    OPEN = 2
    PENDING = 3
    RESOLVED = 4
    CLOSED = 5

class TicketPriority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class AgentTicketScope(IntEnum):
    GLOBAL_ACCESS = 1
    GROUP_ACCESS = 2
    RESTRICTED_ACCESS = 3

class ContactLanguage(str, Enum):
    ARABIC = "ar"
    BULGARIAN = "bg"
    CATALAN = "ca"
    CHINESE_CHINA = "zh-CN"
    CHINESE_TAIWAN = "zh-TW"
    CROATIAN = "hr"
    CZECH = "cs"
    DANISH = "da"
    DUTCH = "nl"
    ENGLISH = "en"
    ESTONIAN = "et"
    FINNISH = "fi"
    FRENCH = "fr"
    GERMAN = "de"
    GREEK = "el"
    HEBREW = "he"
    HUNGARIAN = "hu"
    INDONESIAN = "id"
    ITALIAN = "it"
    JAPANESE = "ja"
    KOREAN = "ko"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    NORWEGIAN = "no"
    POLISH = "pl"
    PORTUGUESE_BRAZIL = "pt-BR"
    PORTUGUESE_PORTUGAL = "pt-PT"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    SPANISH_LATIN_AMERICA = "es-LA"
    SPANISH_SPAIN = "es"
    SWEDISH = "sv"
    THAI = "th"
    TURKISH = "tr"
    UKRAINIAN = "uk"
    VIETNAMESE = "vi"

class UnassignedForOptions(str, Enum):
    THIRTY_MIN = "30m"
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    FOUR_HOURS = "4h"
    EIGHT_HOURS = "8h"
    TWELVE_HOURS = "12h"
    ONE_DAY = "1d"
    TWO_DAYS = "2d"
    THREE_DAYS = "3d"

class GroupCreate(BaseModel):
    name: str = Field(..., description="Name of the group")
    description: Optional[str] = Field(None, description="Description of the group")
    agent_ids: Optional[List[int]] = Field(
        default=None,
        description="Array of agent user ids"
    )
    auto_ticket_assign: Optional[int] = Field(
        default=0,
        ge=0,
        le=1,
        description="Automatic ticket assignment type (0 or 1)"
    )
    escalate_to: Optional[int] = Field(
        None,
        description="User ID to whom escalation email is sent if ticket is unassigned"
    )
    unassigned_for: Optional[UnassignedForOptions] = Field(
        default=UnassignedForOptions.THIRTY_MIN,
        description="Time after which escalation email will be sent"
    )

class ContactCreate(BaseModel):
    name: str = Field(..., description="Name of the contact")
    email: Optional[str] = Field(None, description="Email address of the contact")
    phone: Optional[str] = Field(None, description="Telephone number of the contact")
    mobile: Optional[str] = Field(None, description="Mobile number of the contact")
    twitter_id: Optional[str] = Field(None, description="Twitter handle of the contact")
    unique_external_id: Optional[str] = Field(None, description="External ID of the contact")
    address: Optional[str] = Field(None, description="Address of the contact")
    avatar: Optional[str] = Field(None, description="Path to avatar image file for upload. If provided, request becomes multipart/form-data.")
    company_id: Optional[int] = Field(None, description="ID of the company to which the contact belongs")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Key-value pairs of custom fields")
    description: Optional[str] = Field(None, description="A short description of the contact")
    job_title: Optional[str] = Field(None, description="Job title of the contact")
    language: Optional[ContactLanguage] = Field(None, description="Language of the contact")
    tags: Optional[List[str]] = Field(None, description="Tags associated with the contact")
    time_zone: Optional[str] = Field(None, description="Time zone of the contact")
    other_emails: Optional[List[str]] = Field(None, description="Additional email addresses for the contact")
    lookup_parameter: Optional[str] = Field(None, description="Parameter for identifying existing contacts (e.g., email, mobile, phone, unique_external_id)")


class ContactFieldCreate(BaseModel):
    label: str = Field(..., description="Display name for the field (as seen by agents)")
    label_for_customers: str = Field(..., description="Display name for the field (as seen by customers)")
    type: str = Field(
        ...,
        description="Type of the field",
        pattern="^(custom_text|custom_paragraph|custom_checkbox|custom_number|custom_dropdown|custom_phone_number|custom_url|custom_date)$"
    )
    editable_in_signup: bool = Field(
        default=False,
        description="Set to true if the field can be updated by customers during signup"
    )
    position: int = Field(
        default=1,
        description="Position of the company field"
    )
    required_for_agents: bool = Field(
        default=False,
        description="Set to true if the field is mandatory for agents"
    )
    customers_can_edit: bool = Field(
        default=False,
        description="Set to true if the customer can edit the fields in the customer portal"
    )
    required_for_customers: bool = Field(
        default=False,
        description="Set to true if the field is mandatory in the customer portal"
    )
    displayed_for_customers: bool = Field(
        default=False,
        description="Set to true if the customers can see the field in the customer portal"
    )
    choices: Optional[List[Dict[str, Union[str, int]]]] = Field(
        default=None,
        description="Array of objects in format {'value': 'Choice text', 'position': 1} for dropdown choices"
    )

class CannedResponseCreate(BaseModel):
    title: str = Field(..., description="Title of the canned response")
    content_html: str = Field(..., description="HTML version of the canned response content")
    folder_id: int = Field(..., description="Folder where the canned response gets added")
    visibility: int = Field(
        ...,
        description="Visibility of the canned response (0=all agents, 1=personal, 2=select groups)",
        ge=0,
        le=2
    )
    group_ids: Optional[List[int]] = Field(
        None,
        description="Groups for which the canned response is visible. Required if visibility=2"
    )

class MakeAgent(BaseModel):
    occasional: Optional[bool] = Field(None, description="Set to true if the agent is an occasional agent")
    ticket_scope: AgentTicketScope = Field(..., description="Ticket scope of the agent")
    group_ids: Optional[List[int]] = Field(None, description="Array of Group IDs that the agent has access to")
    role_ids: Optional[List[int]] = Field(None, description="Array of Role IDs that are associated with the agent")
    skill_ids: Optional[List[int]] = Field(None, description="Array of Skill IDs that are associated with the agent")
    department_ids: Optional[List[int]] = Field(None, description="Array of Department IDs to which the agent is associated")

class CompanyCreate(BaseModel):
    name: str = Field(..., description="Name of the company")
    description: Optional[str] = Field(None, description="A short description of the company")
    domains: Optional[List[str]] = Field(None, description="List of domains associated with the company")
    note: Optional[str] = Field(None, description="A note about the company")
    health_score: Optional[str] = Field(None, description="Health score of the company")
    account_tier: Optional[str] = Field(None, description="Account tier of the company")
    renewal_date: Optional[str] = Field(None, description="Renewal date for the company's contract (YYYY-MM-DD)") # Consider date validation if needed
    industry: Optional[str] = Field(None, description="Industry to which the company belongs")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Key-value pairs of custom fields for the company")

class CompanyFieldCreate(BaseModel):
    label: str = Field(..., description="Label for the company field")
    type: str = Field(
        ...,
        description="Type of the company field",
        # Regex for Freshdesk supported company field types based on typical patterns
        # This might need adjustment if Freshdesk has a very specific list or different naming
        pattern="^(custom_text|custom_paragraph|custom_number|custom_date|custom_checkbox|custom_dropdown|custom_url)$"
    )
    position: Optional[int] = Field(None, description="Position of the company field among other fields")
    required_for_agents: Optional[bool] = Field(False, description="Set to true if the field is mandatory for agents")
    # Making choices more specific for creation - value is required.
    choices: Optional[List[Dict[str, Union[str, int]]]] = Field(
        None,
        description="Array of choices for dropdown fields. Each dict should have 'value' and optionally 'position'."
    )
    # Add other common fields if necessary, based on Freshdesk API for company fields
    # For example: displayed_for_customers, customers_can_edit (if applicable to company fields)

class CompanyFieldUpdate(BaseModel):
    label: Optional[str] = Field(None, description="Label for the company field")
    # Type is usually not updatable, but including it as optional if API allows
    type: Optional[str] = Field(
        None,
        description="Type of the company field",
        pattern="^(custom_text|custom_paragraph|custom_number|custom_date|custom_checkbox|custom_dropdown|custom_url)$"
    )
    position: Optional[int] = Field(None, description="Position of the company field among other fields")
    required_for_agents: Optional[bool] = Field(None, description="Set to true if the field is mandatory for agents")
    # For choices, Freshdesk API might require specific handling for updating/deleting choices (e.g., by ID)
    # This model assumes choices are replaced or new ones added. Check API for partial updates to choices.
    choices: Optional[List[Dict[str, Union[str, int]]]] = Field(
        None,
        description="Array of choices for dropdown fields. Each dict should have 'value' and optionally 'position'."
    )

@mcp.tool()
async def get_ticket_fields() -> Dict[str, Any]:
    """Get ticket fields from Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/ticket_fields"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()


@mcp.tool()
async def get_tickets(page: Optional[int] = 1, per_page: Optional[int] = 30) -> Dict[str, Any]:
    """Get tickets from Freshdesk with pagination support."""
    # Validate input parameters
    if page < 1:
        return {"error": "Page number must be greater than 0"}

    if per_page < 1 or per_page > 100:
        return {"error": "Page size must be between 1 and 100"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets"

    params = {
        "page": page,
        "per_page": per_page
    }

    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

            # Parse pagination from Link header
            link_header = response.headers.get('Link', '')
            pagination_info = parse_link_header(link_header)

            tickets = response.json()

            return {
                "tickets": tickets,
                "pagination": {
                    "current_page": page,
                    "next_page": pagination_info.get("next"),
                    "prev_page": pagination_info.get("prev"),
                    "per_page": per_page
                }
            }

        except httpx.HTTPStatusError as e:
            return {"error": f"Failed to fetch tickets: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def create_ticket(
    subject: str,
    description: str,
    source: Union[int, str],
    priority: Union[int, str],
    status: Union[int, str],
    email: Optional[str] = None,
    requester_id: Optional[int] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    additional_fields: Optional[Dict[str, Any]] = None  # 👈 new parameter
) -> str:
    """Create a ticket in Freshdesk"""
    # Validate requester information
    if not email and not requester_id:
        return "Error: Either email or requester_id must be provided"

    # Convert string inputs to integers if necessary
    try:
        source_val = int(source)
        priority_val = int(priority)
        status_val = int(status)
    except ValueError:
        return "Error: Invalid value for source, priority, or status"

    # Validate enum values
    if (source_val not in [e.value for e in TicketSource] or
        priority_val not in [e.value for e in TicketPriority] or
        status_val not in [e.value for e in TicketStatus]):
        return "Error: Invalid value for source, priority, or status"

    # Prepare the request data
    data = {
        "subject": subject,
        "description": description,
        "source": source_val,
        "priority": priority_val,
        "status": status_val
    }

    # Add requester information
    if email:
        data["email"] = email
    if requester_id:
        data["requester_id"] = requester_id

    # Add custom fields if provided
    if custom_fields:
        data["custom_fields"] = custom_fields

     # Add any other top-level fields
    if additional_fields:
        data.update(additional_fields)

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()

            if response.status_code == 201:
                return "Ticket created successfully"

            response_data = response.json()
            return f"Success: {response_data}"

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                # Handle validation errors and check for mandatory custom fields
                error_data = e.response.json()
                if "errors" in error_data:
                    return f"Validation Error: {error_data['errors']}"
            return f"Error: Failed to create ticket - {str(e)}"
        except Exception as e:
            return f"Error: An unexpected error occurred - {str(e)}"

@mcp.tool()
async def update_ticket(ticket_id: int, ticket_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Update a ticket in Freshdesk."""
    if not ticket_fields:
        return {"error": "No fields provided for update"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    # Separate custom fields from standard fields
    custom_fields = ticket_fields.pop('custom_fields', {})

    # Prepare the update data
    update_data = {}

    # Add standard fields if they are provided
    for field, value in ticket_fields.items():
        update_data[field] = value

    # Add custom fields if they exist
    if custom_fields:
        update_data['custom_fields'] = custom_fields

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers, json=update_data)
            response.raise_for_status()

            return {
                "success": True,
                "message": "Ticket updated successfully",
                "ticket": response.json()
            }

        except httpx.HTTPStatusError as e:
            error_message = f"Failed to update ticket: {str(e)}"
            try:
                error_details = e.response.json()
                if "errors" in error_details:
                    error_message = f"Validation errors: {error_details['errors']}"
            except Exception:
                pass
            return {
                "success": False,
                "error": error_message
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"An unexpected error occurred: {str(e)}"
            }

@mcp.tool()
async def delete_ticket(ticket_id: int) -> str:
    """Delete a ticket in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers)
        return response.json()

@mcp.tool()
async def get_ticket(ticket_id: int):
    """Get a ticket in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def search_tickets(query: str) -> Dict[str, Any]:
    """Search for tickets in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/search/tickets"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    params = {"query": query}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        return response.json()

@mcp.tool()
async def get_ticket_conversation(ticket_id: int)-> list[Dict[str, Any]]:
    """Get a ticket conversation in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}/conversations"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def create_ticket_reply(ticket_id: int,body: str)-> Dict[str, Any]:
    """Create a reply to a ticket in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}/reply"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    data = {
        "body": body
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response.json()

@mcp.tool()
async def create_ticket_note(ticket_id: int,body: str)-> Dict[str, Any]:
    """Create a note for a ticket in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}/notes"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    data = {
        "body": body
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response.json()

@mcp.tool()
async def update_ticket_conversation(conversation_id: int,body: str)-> Dict[str, Any]:
    """Update a conversation for a ticket in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/conversations/{conversation_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    data = {
        "body": body
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=data)
        status_code = response.status_code
        if status_code == 200:
            return response.json()
        else:
            return f"Cannot update conversation ${response.json()}"

@mcp.tool()
async def get_agents(page: Optional[int] = 1, per_page: Optional[int] = 30)-> list[Dict[str, Any]]:
    """Get all agents in Freshdesk with pagination support."""
    # Validate input parameters
    if page < 1:
        return {"error": "Page number must be greater than 0"}

    if per_page < 1 or per_page > 100:
        return {"error": "Page size must be between 1 and 100"}
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/agents"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    params = {
        "page": page,
        "per_page": per_page
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        return response.json()

@mcp.tool()
async def list_contacts(page: Optional[int] = 1, per_page: Optional[int] = 30)-> list[Dict[str, Any]]:
    """List all contacts in Freshdesk with pagination support."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    params = {
        "page": page,
        "per_page": per_page
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        return response.json()

@mcp.tool()
async def get_contact(contact_id: int)-> Dict[str, Any]:
    """Get a contact in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts/{contact_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def search_contacts(query: str)-> list[Dict[str, Any]]:
    """Search for contacts in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts/autocomplete"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    params = {"term": query}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        return response.json()

@mcp.tool()
async def update_contact(contact_id: int, contact_fields: Dict[str, Any])-> Dict[str, Any]:
    """Update a contact in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts/{contact_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    data = {}
    for field, value in contact_fields.items():
        data[field] = value
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=data)
        return response.json()


@mcp.tool()
async def create_contact(contact_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Create a contact in Freshdesk.
    Handles JSON or multipart/form-data requests based on 'avatar' presence.
    """
    try:
        # Validate that at least one identifier is present along with name
        if not contact_fields.get("name"):
            return {"error": "Name is a required field for creating a contact."}

        required_one_of = ["email", "phone", "mobile", "twitter_id", "unique_external_id"]
        if not any(contact_fields.get(field) for field in required_one_of):
            return {"error": f"At least one of {', '.join(required_one_of)} must be provided."}

        validated_fields = ContactCreate(**contact_fields)
        contact_data = validated_fields.model_dump(exclude_none=True)

    except Exception as e: # Pydantic's ValidationError
        return {"error": f"Validation error: {str(e)}"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }

    avatar_path = contact_data.pop("avatar", None)

    async with httpx.AsyncClient() as client:
        try:
            if avatar_path:
                if not os.path.exists(avatar_path):
                    return {"error": f"Avatar file not found at path: {avatar_path}"}
                files = {'avatar': (os.path.basename(avatar_path), open(avatar_path, 'rb'))}
                # httpx will set Content-Type to multipart/form-data
                # For multipart, data should be passed to 'data' param, not 'json'
                response = await client.post(url, headers=headers, data=contact_data, files=files)
            else:
                headers["Content-Type"] = "application/json"
                response = await client.post(url, headers=headers, json=contact_data)

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to create contact: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to create contact: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}


@mcp.tool()
async def delete_contact(contact_id: int) -> Dict[str, Any]:
    """Soft delete a contact in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts/{contact_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers)
            if response.status_code == 204:
                return {"success": True, "message": f"Contact {contact_id} deleted successfully."}
            response.raise_for_status() # Should not happen if 204 is success
            return response.json() # Should not happen
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to delete contact {contact_id}: {str(e)}", "details": error_details}
            except Exception:
                 return {"error": f"Failed to delete contact {contact_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while deleting contact {contact_id}: {str(e)}"}


@mcp.tool()
async def hard_delete_contact(contact_id: int, force: Optional[bool] = False) -> Dict[str, Any]:
    """Hard delete a contact in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts/{contact_id}/hard_delete"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    params = {}
    if force:
        params["force"] = "true"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers, params=params)
            if response.status_code == 204:
                return {"success": True, "message": f"Contact {contact_id} hard deleted successfully."}
            response.raise_for_status()
            return response.json() # Should not happen
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to hard delete contact {contact_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to hard delete contact {contact_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while hard deleting contact {contact_id}: {str(e)}"}


@mcp.tool()
async def make_agent_from_contact(contact_id: int, agent_details: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a contact into an agent in Freshdesk."""
    if not agent_details:
        return {"error": "agent_details cannot be empty."}

    try:
        validated_details = MakeAgent(**agent_details)
        request_data = validated_details.model_dump(exclude_none=True)
    except Exception as e: # Pydantic's ValidationError
        return {"error": f"Validation error for agent_details: {str(e)}"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts/{contact_id}/make_agent"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers, json=request_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to make agent from contact {contact_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to make agent from contact {contact_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while making agent from contact {contact_id}: {str(e)}"}


@mcp.tool()
async def restore_contact(contact_id: int) -> Dict[str, Any]:
    """Restore a soft-deleted contact in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts/{contact_id}/restore"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers) # No body needed for restore
            if response.status_code == 204:
                return {"success": True, "message": f"Contact {contact_id} restored successfully."}
            response.raise_for_status()
            return response.json() # Should not happen
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to restore contact {contact_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to restore contact {contact_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while restoring contact {contact_id}: {str(e)}"}


@mcp.tool()
async def send_invite_to_contact(contact_id: int) -> Dict[str, Any]:
    """Send an invitation email to a contact in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contacts/{contact_id}/send_invite"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers) # No body needed for sending invite
            if response.status_code == 204: # Freshdesk API doc says 200 OK, but it's typically 204 for no content actions
                return {"success": True, "message": f"Invitation sent to contact {contact_id} successfully."}
            # Handle 200 OK if that's what API returns
            if response.status_code == 200:
                 return {"success": True, "message": f"Invitation sent to contact {contact_id} successfully.", "details": response.json()}
            response.raise_for_status()
            return response.json() # Should not happen if 204 or 200
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to send invite to contact {contact_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to send invite to contact {contact_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while sending invite to contact {contact_id}: {str(e)}"}


@mcp.tool()
async def list_canned_responses(folder_id: int)-> list[Dict[str, Any]]:
    """List all canned responses in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/canned_response_folders/{folder_id}/responses"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    canned_responses = []
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        for canned_response in response.json():
            canned_responses.append(canned_response)
    return canned_responses

@mcp.tool()
async def list_canned_response_folders()-> list[Dict[str, Any]]:
    """List all canned response folders in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/canned_response_folders"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def view_canned_response(canned_response_id: int)-> Dict[str, Any]:
    """View a canned response in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/canned_responses/{canned_response_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()
@mcp.tool()
async def create_canned_response(canned_response_fields: Dict[str, Any])-> Dict[str, Any]:
    """Create a canned response in Freshdesk."""
    # Validate input using Pydantic model
    try:
        validated_fields = CannedResponseCreate(**canned_response_fields)
        # Convert to dict for API request
        canned_response_data = validated_fields.model_dump(exclude_none=True)
    except Exception as e:
        return {"error": f"Validation error: {str(e)}"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/canned_responses"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=canned_response_data)
        return response.json()

@mcp.tool()
async def update_canned_response(canned_response_id: int, canned_response_fields: Dict[str, Any])-> Dict[str, Any]:
    """Update a canned response in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/canned_responses/{canned_response_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=canned_response_fields)
        return response.json()
@mcp.tool()
async def create_canned_response_folder(name: str)-> Dict[str, Any]:
    """Create a canned response folder in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/canned_response_folders"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    data = {
        "name": name
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response.json()
@mcp.tool()
async def update_canned_response_folder(folder_id: int, name: str)-> Dict[str, Any]:
    """Update a canned response folder in Freshdesk."""
    print(folder_id, name)
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/canned_response_folders/{folder_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    data = {
        "name": name
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=data)
        return response.json()

@mcp.tool()
async def list_solution_articles(folder_id: int)-> list[Dict[str, Any]]:
    """List all solution articles in Freshdesk."""
    solution_articles = []
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/folders/{folder_id}/articles"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        for article in response.json():
            solution_articles.append(article)
    return solution_articles

@mcp.tool()
async def list_solution_folders(category_id: int)-> list[Dict[str, Any]]:
    if not category_id:
        return {"error": "Category ID is required"}
    """List all solution folders in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/categories/{category_id}/folders"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def list_solution_categories()-> list[Dict[str, Any]]:
    """List all solution categories in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/categories"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def view_solution_category(category_id: int)-> Dict[str, Any]:
    """View a solution category in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/categories/{category_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def create_solution_category(category_fields: Dict[str, Any])-> Dict[str, Any]:
    """Create a solution category in Freshdesk."""
    if not category_fields.get("name"):
        return {"error": "Name is required"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/categories"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=category_fields)
        return response.json()

@mcp.tool()
async def update_solution_category(category_id: int, category_fields: Dict[str, Any])-> Dict[str, Any]:
    """Update a solution category in Freshdesk."""
    if not category_fields.get("name"):
        return {"error": "Name is required"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/categories/{category_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=category_fields)
        return response.json()

@mcp.tool()
async def create_solution_category_folder(category_id: int, folder_fields: Dict[str, Any])-> Dict[str, Any]:
    """Create a solution category folder in Freshdesk."""
    if not folder_fields.get("name"):
        return {"error": "Name is required"}
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/categories/{category_id}/folders"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=folder_fields)
        return response.json()

@mcp.tool()
async def view_solution_category_folder(folder_id: int)-> Dict[str, Any]:
    """View a solution category folder in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/folders/{folder_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()
@mcp.tool()
async def update_solution_category_folder(folder_id: int, folder_fields: Dict[str, Any])-> Dict[str, Any]:
    """Update a solution category folder in Freshdesk."""
    if not folder_fields.get("name"):
        return {"error": "Name is required"}
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/folders/{folder_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=folder_fields)
        return response.json()


@mcp.tool()
async def create_solution_article(folder_id: int, article_fields: Dict[str, Any])-> Dict[str, Any]:
    """Create a solution article in Freshdesk."""
    if not article_fields.get("title") or not article_fields.get("status") or not article_fields.get("description"):
        return {"error": "Title, status and description are required"}
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/folders/{folder_id}/articles"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=article_fields)
        return response.json()

@mcp.tool()
async def view_solution_article(article_id: int)-> Dict[str, Any]:
    """View a solution article in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/articles/{article_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def update_solution_article(article_id: int, article_fields: Dict[str, Any])-> Dict[str, Any]:
    """Update a solution article in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/solutions/articles/{article_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=article_fields)
        return response.json()

@mcp.tool()
async def view_agent(agent_id: int)-> Dict[str, Any]:
    """View an agent in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/agents/{agent_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def create_agent(agent_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Create an agent in Freshdesk."""
    # Validate mandatory fields
    if not agent_fields.get("email") or not agent_fields.get("ticket_scope"):
        return {
            "error": "Missing mandatory fields. Both 'email' and 'ticket_scope' are required."
        }
    if agent_fields.get("ticket_scope") not in [e.value for e in AgentTicketScope]:
        return {
            "error": "Invalid value for ticket_scope. Must be one of: " + ", ".join([e.name for e in AgentTicketScope])
        }

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/agents"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=agent_fields)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"Failed to create agent: {str(e)}",
                "details": e.response.json() if e.response else None
            }

@mcp.tool()
async def update_agent(agent_id: int, agent_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Update an agent in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/agents/{agent_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=agent_fields)
        return response.json()

@mcp.tool()
async def search_agents(query: str) -> list[Dict[str, Any]]:
    """Search for agents in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/agents/autocomplete?term={query}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def delete_agent(agent_id: int) -> Dict[str, Any]:
    """Delete an agent in Freshdesk. Deleting an agent downgrades them to a contact."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/agents/{agent_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers)
            if response.status_code == 204:
                return {"message": f"Agent {agent_id} deleted successfully and downgraded to contact."}
            response.raise_for_status()
            # Should not be reached if 204 is success and other errors are raised
            return {"error": f"Unexpected status code {response.status_code}", "details": response.text}
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to delete agent {agent_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to delete agent {agent_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while deleting agent {agent_id}: {str(e)}"}

@mcp.tool()
async def get_current_agent() -> Dict[str, Any]:
    """Get details of the currently authenticated agent in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/agents/me"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to get current agent: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to get current agent: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while getting current agent: {str(e)}"}

@mcp.tool()
async def list_groups(page: Optional[int] = 1, per_page: Optional[int] = 30)-> list[Dict[str, Any]]:
    """List all groups in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/groups"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    params = {
        "page": page,
        "per_page": per_page
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        return response.json()

@mcp.tool()
async def view_role(role_id: int) -> Dict[str, Any]:
    """View a specific role in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/roles/{role_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to view role {role_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to view role {role_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while viewing role {role_id}: {str(e)}"}

@mcp.tool()
async def list_roles() -> Dict[str, Any]: # Corrected return type to Dict, assuming Freshdesk returns a dict with a 'roles' key or similar
    """List all roles in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/roles"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            # Typically, list endpoints return a dictionary like {"roles": [...]} or directly a list.
            # Assuming it's a dictionary for consistency with other list functions.
            # If API returns a list directly, this can be adjusted.
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to list roles: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to list roles: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while listing roles: {str(e)}"}

@mcp.tool()
async def view_product(product_id: int) -> Dict[str, Any]:
    """View a specific product in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/products/{product_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to view product {product_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to view product {product_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while viewing product {product_id}: {str(e)}"}

@mcp.tool()
async def list_products() -> Dict[str, Any]: # Freshdesk typically returns a list, but wrapping in Dict for consistency if it's {"products": [...]} or directly a list.
    """List all products in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/products"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            # The API returns a list of products directly.
            # To maintain consistency with other list functions that might return a dict (e.g. with pagination),
            # we can return it as {"products": response.json()} or adjust the return type hint to List[Dict[str, Any]].
            # For now, returning the direct JSON which is List[Dict[str, Any]].
            # The type hint Dict[str, Any] is a bit general if it's a direct list.
            # Let's assume it might be a list or a dict like {"products": []}
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to list products: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to list products: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while listing products: {str(e)}"}

@mcp.tool()
async def create_group(group_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Create a group in Freshdesk."""
    # Validate input using Pydantic model
    try:
        validated_fields = GroupCreate(**group_fields)
        # Convert to dict for API request
        group_data = validated_fields.model_dump(exclude_none=True)
    except Exception as e:
        return {"error": f"Validation error: {str(e)}"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/groups"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=group_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"Failed to create group: {str(e)}",
                "details": e.response.json() if e.response else None
            }

@mcp.tool()
async def view_group(group_id: int) -> Dict[str, Any]:
    """View a group in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/groups/{group_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def create_ticket_field(ticket_field_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Create a ticket field in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/admin/ticket_fields"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=ticket_field_fields)
        return response.json()
@mcp.tool()
async def view_ticket_field(ticket_field_id: int) -> Dict[str, Any]:
    """View a ticket field in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/admin/ticket_fields/{ticket_field_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def update_ticket_field(ticket_field_id: int, ticket_field_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Update a ticket field in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/admin/ticket_fields/{ticket_field_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=ticket_field_fields)
        return response.json()

@mcp.tool()
async def delete_ticket_field(ticket_field_id: int) -> Dict[str, Any]:
    """Delete a ticket field in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/admin/ticket_fields/{ticket_field_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers)
            if response.status_code == 204:
                return {"message": f"Ticket field {ticket_field_id} deleted successfully"}
            response.raise_for_status()
            # Should not be reached if 204 is success and other errors are raised
            return {"error": f"Unexpected status code {response.status_code}", "details": response.text}
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to delete ticket field {ticket_field_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to delete ticket field {ticket_field_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while deleting ticket field {ticket_field_id}: {str(e)}"}

@mcp.tool()
async def update_group(group_id: int, group_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Update a group in Freshdesk."""
    try:
        validated_fields = GroupCreate(**group_fields)
        # Convert to dict for API request
        group_data = validated_fields.model_dump(exclude_none=True)
    except Exception as e:
        return {"error": f"Validation error: {str(e)}"}
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/groups/{group_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers, json=group_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"Failed to update group: {str(e)}",
                "details": e.response.json() if e.response else None
            }

@mcp.tool()
async def list_contact_fields()-> list[Dict[str, Any]]:
    """List all contact fields in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contact_fields"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def view_contact_field(contact_field_id: int) -> Dict[str, Any]:
    """View a contact field in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contact_fields/{contact_field_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        return response.json()

@mcp.tool()
async def create_contact_field(contact_field_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Create a contact field in Freshdesk."""
    # Validate input using Pydantic model
    try:
        validated_fields = ContactFieldCreate(**contact_field_fields)
        # Convert to dict for API request
        contact_field_data = validated_fields.model_dump(exclude_none=True)
    except Exception as e:
        return {"error": f"Validation error: {str(e)}"}
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contact_fields"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=contact_field_data)
        return response.json()

@mcp.tool()
async def update_contact_field(contact_field_id: int, contact_field_fields: Dict[str, Any]) -> Dict[str, Any]:
    """Update a contact field in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contact_fields/{contact_field_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=contact_field_fields)
        return response.json()

@mcp.tool()
async def delete_contact_field(contact_field_id: int) -> Dict[str, Any]:
    """Delete a contact field in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/contact_field/{contact_field_id}" # Note: singular 'contact_field'
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers)
            if response.status_code == 204:
                return {"message": f"Contact field {contact_field_id} deleted successfully"}
            response.raise_for_status()
            # Should not be reached if 204 is success and other errors are raised
            return {"error": f"Unexpected status code {response.status_code}", "details": response.text}
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to delete contact field {contact_field_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to delete contact field {contact_field_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while deleting contact field {contact_field_id}: {str(e)}"}

@mcp.tool()
async def get_field_properties(field_name: str):
    """Get properties of a specific field by name."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/ticket_fields"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }
    actual_field_name=field_name
    if field_name == "type":
        actual_field_name="ticket_type"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()  # Raise error for bad status codes
        fields = response.json()
    # Filter the field by name
    matched_field = next((field for field in fields if field["name"] == actual_field_name), None)

    return matched_field

@mcp.prompt()
def create_ticket(
    subject: str,
    description: str,
    source: str,
    priority: str,
    status: str,
    email: str
) -> str:
    """Create a ticket in Freshdesk"""
    payload = {
        "subject": subject,
        "description": description,
        "source": source,
        "priority": priority,
        "status": status,
        "email": email,
    }
    return f"""
Kindly create a ticket in Freshdesk using the following payload:

{payload}

If you need to retrieve information about any fields (such as allowed values or internal keys), please use the `get_field_properties()` function.

Notes:
- The "type" field is **not** a custom field; it is a standard system field.
- The "type" field is required but should be passed as a top-level parameter, not within custom_fields.
Make sure to reference the correct keys from `get_field_properties()` when constructing the payload.
"""

@mcp.prompt()
def create_reply(
    ticket_id:int,
    reply_message: str,
) -> str:
    """Create a reply in Freshdesk"""
    payload = {
        "body":reply_message,
    }
    return f"""
Kindly create a ticket reply in Freshdesk for ticket ID {ticket_id} using the following payload:

{payload}

Notes:
- The "body" field must be in **HTML format** and should be **brief yet contextually complete**.
- When composing the "body", please **review the previous conversation** in the ticket.
- Ensure the tone and style **match the prior replies**, and that the message provides **full context** so the recipient can understand the issue without needing to re-read earlier messages.
"""

@mcp.tool()
async def list_companies(page: Optional[int] = 1, per_page: Optional[int] = 30) -> Dict[str, Any]:
    """List all companies in Freshdesk with pagination support."""
    # Validate input parameters
    if page < 1:
        return {"error": "Page number must be greater than 0"}

    if per_page < 1 or per_page > 100:
        return {"error": "Page size must be between 1 and 100"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/companies"

    params = {
        "page": page,
        "per_page": per_page
    }

    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

            # Parse pagination from Link header
            link_header = response.headers.get('Link', '')
            pagination_info = parse_link_header(link_header)

            companies = response.json()

            return {
                "companies": companies,
                "pagination": {
                    "current_page": page,
                    "next_page": pagination_info.get("next"),
                    "prev_page": pagination_info.get("prev"),
                    "per_page": per_page
                }
            }

        except httpx.HTTPStatusError as e:
            return {"error": f"Failed to fetch companies: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def create_company(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a company in Freshdesk.
    The 'name' field is mandatory.
    """
    try:
        if not company_data.get("name"):
            return {"error": "The 'name' field is mandatory for creating a company."}
        
        validated_data = CompanyCreate(**company_data)
        request_data = validated_data.model_dump(exclude_none=True)
    except Exception as e: # Pydantic's ValidationError
        return {"error": f"Validation error: {str(e)}"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/companies"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=request_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to create company: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to create company: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while creating company: {str(e)}"}

@mcp.tool()
async def delete_company(company_id: int) -> Dict[str, Any]:
    """Delete a company in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/companies/{company_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json" # Though not strictly needed for DELETE, it's good practice
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers)
            if response.status_code == 204:
                return {"success": True, "message": f"Company {company_id} deleted successfully."}
            response.raise_for_status() # Will raise for other errors
            # Should not be reached if 204 is success and other errors are raised
            return {"error": f"Unexpected status code {response.status_code}", "details": response.text}
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to delete company {company_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to delete company {company_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while deleting company {company_id}: {str(e)}"}


@mcp.tool()
async def view_company(company_id: int) -> Dict[str, Any]:
    """Get a company in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/companies/{company_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"Failed to fetch company: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def search_companies(query: str) -> Dict[str, Any]:
    """Search for companies in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/companies/autocomplete"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    # Use the name parameter as specified in the API
    params = {"name": query}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"Failed to search companies: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def find_company_by_name(name: str) -> Dict[str, Any]:
    """Find a company by name in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/companies/autocomplete"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    params = {"name": name}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"Failed to find company: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def create_company_field(field_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a custom company field in Freshdesk."""
    try:
        if not field_data.get("label") or not field_data.get("type"):
            return {"error": "The 'label' and 'type' fields are mandatory."}
        
        validated_data = CompanyFieldCreate(**field_data)
        request_data = validated_data.model_dump(exclude_none=True)
    except Exception as e: # Pydantic's ValidationError
        return {"error": f"Validation error: {str(e)}"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/company_fields"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=request_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to create company field: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to create company field: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while creating company field: {str(e)}"}

@mcp.tool()
async def view_company_field(field_id: int) -> Dict[str, Any]:
    """View a specific custom company field in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/company_fields/{field_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to view company field {field_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to view company field {field_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while viewing company field {field_id}: {str(e)}"}

@mcp.tool()
async def update_company_field(field_id: int, field_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update a custom company field in Freshdesk.
    Note: API path uses singular 'company_field'.
    """
    try:
        validated_data = CompanyFieldUpdate(**field_data)
        request_data = validated_data.model_dump(exclude_none=True)
        if not request_data:
             return {"error": "No update data provided."}
    except Exception as e: # Pydantic's ValidationError
        return {"error": f"Validation error: {str(e)}"}

    url = f"https://{FRESHDESK_DOMAIN}/api/v2/company_field/{field_id}" # Singular 'company_field'
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers, json=request_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to update company field {field_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to update company field {field_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while updating company field {field_id}: {str(e)}"}

@mcp.tool()
async def delete_company_field(field_id: int) -> Dict[str, Any]:
    """Delete a custom company field in Freshdesk.
    Note: API path uses singular 'company_field'.
    """
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/company_field/{field_id}" # Singular 'company_field'
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers)
            if response.status_code == 204:
                return {"success": True, "message": f"Company field {field_id} deleted successfully."}
            response.raise_for_status()
            # Should not be reached if 204 is success
            return {"error": f"Unexpected status code {response.status_code}", "details": response.text}
        except httpx.HTTPStatusError as e:
            try:
                error_details = e.response.json()
                return {"error": f"Failed to delete company field {field_id}: {str(e)}", "details": error_details}
            except Exception:
                return {"error": f"Failed to delete company field {field_id}: {str(e)}, response: {e.response.text}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred while deleting company field {field_id}: {str(e)}"}


@mcp.tool()
async def list_company_fields() -> List[Dict[str, Any]]:
    """List all company fields in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/company_fields"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"Failed to fetch company fields: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def view_ticket_summary(ticket_id: int) -> Dict[str, Any]:
    """Get the summary of a ticket in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}/summary"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"Failed to fetch ticket summary: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def update_ticket_summary(ticket_id: int, body: str) -> Dict[str, Any]:
    """Update the summary of a ticket in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}/summary"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }
    data = {
        "body": body
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"Failed to update ticket summary: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.tool()
async def delete_ticket_summary(ticket_id: int) -> Dict[str, Any]:
    """Delete the summary of a ticket in Freshdesk."""
    url = f"https://{FRESHDESK_DOMAIN}/api/v2/tickets/{ticket_id}/summary"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{FRESHDESK_API_KEY}:X'.encode()).decode()}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers)
            if response.status_code == 204:
                return {"success": True, "message": "Ticket summary deleted successfully"}

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"Failed to delete ticket summary: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

def main():
    logging.info("Starting Freshdesk MCP server")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
