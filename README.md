# Freshdesk MCP Server
[![smithery badge](https://smithery.ai/badge/@effytech/freshdesk_mcp)](https://smithery.ai/server/@effytech/freshdesk_mcp)

An MCP server implementation that integrates with Freshdesk, enabling AI models to interact with Freshdesk modules and perform various support operations.

## Features

- **Freshdesk Integration**: Seamless interaction with Freshdesk API endpoints
- **AI Model Support**: Enables AI models to perform support operations through Freshdesk
- **Automated Ticket Management**: Handle ticket creation, updates, and responses
- **Advanced Search Capabilities**: Comprehensive ticket search with helper functions for complex queries

## Components

### Tools

The server offers several tools for Freshdesk operations:

- `create_ticket`: Create new tickets in Freshdesk
- `get_ticket`: Retrieve detailed information about a specific ticket
- `update_ticket`: Update ticket properties and fields
- `get_ticket_conversation`: Retrieve the conversation thread for a ticket
- `update_ticket_conversation`: Add notes or replies to ticket conversations
- `search_tickets`: Search for tickets using Freshdesk's query syntax

### Ticket Search Functionality

The ticket search functionality allows searching for Freshdesk tickets using specific query syntax:

#### Search Query Format

Freshdesk requires a specific format for search queries:

- Format: `"field_name:value AND/OR field_name:'value'"`
- String values must be enclosed in single quotes
- Numeric values should not have quotes
- Boolean values should be `true` or `false` without quotes
- Logical operators (`AND`, `OR`) must be uppercase
- Parentheses can be used to group conditions
- Spaces are required between different conditions and operators

#### Supported Search Fields

Common fields that can be used in searches:

| Field | Type | Description |
| ----- | ---- | ----------- |
| status | integer | Status of the ticket (2=Open, 3=Pending, etc.) |
| priority | integer | Priority of the ticket (1=Low to 4=Urgent) |
| type | string | Type of the ticket ('Question', 'Problem', etc.) |
| tag | string | Tag associated with the ticket |
| agent_id | integer | ID of the agent assigned to the ticket |
| group_id | integer | ID of the group assigned to the ticket |
| created_at | date | Creation date (YYYY-MM-DD) |
| updated_at | date | Last updated date (YYYY-MM-DD) |
| due_by | date | Due date (YYYY-MM-DD) |
| description | string | Text in the ticket description |
| subject | string | Text in the ticket subject |
| cf_* | varies | Custom fields (prefix with cf_) |

#### Search Helper Functions

For convenient search query construction, the following helper functions are provided:

- `build_search_query(field, value, operator)`: Creates a properly formatted search query part
- `build_complex_search_query(*parts, operator)`: Combines multiple query parts into a complex query
- `search_tickets_help()`: Provides detailed documentation on Freshdesk's search query syntax

#### Example Usage

```python
# Simple search for open tickets
search_tickets("status:2")

# Search for high priority open tickets
search_tickets("priority:3 AND status:2")

# Search for tickets with a specific tag
search_tickets("tag:'urgent'")

# Free text search (will automatically search in subject and description)
search_tickets("payment issue")

# Using the helper function to build query parts
status_part = build_search_query("status", 2)  # Returns: status:2
priority_part = build_search_query("priority", 3)  # Returns: priority:3
type_part = build_search_query("type", "Question")  # Returns: type:'Question'
date_part = build_search_query("created_at", "2023-01-01", ">")  # Returns: created_at:>'2023-01-01'

# Combine parts into a complex query
complex_query = build_complex_search_query(status_part, priority_part, operator="AND")
# Returns: (status:2 AND priority:3)

# Search with the complex query
search_result = await search_tickets(complex_query)
```

## Configuration

To use this server, you'll need:

1. A Freshdesk account
2. Freshdesk API key
3. Freshdesk domain

Set the following environment variables:
- `FRESHDESK_API_KEY`: Your Freshdesk API key
- `FRESHDESK_DOMAIN`: Your Freshdesk domain (e.g., `company.freshdesk.com`)

## Development

### Setup

1. Clone the repository
2. Install dependencies
3. Set up environment variables for Freshdesk

### Testing

Run the test scripts to verify functionality:

```bash
python -m tests.test_search_functions
```

## Getting Started

### Installing via Smithery

To install freshdesk_mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@effytech/freshdesk_mcp):

```bash
npx -y @smithery/cli install @effytech/freshdesk_mcp --client claude
```

### Prerequisites

- A Freshdesk account (sign up at [freshdesk.com](https://freshdesk.com))
- Freshdesk API key
- `uvx` installed (`pip install uv` or `brew install uv`)

### Configuration

1. Generate your Freshdesk API key from the Freshdesk admin panel
2. Set up your domain and authentication details

### Usage with Claude Desktop

1. Install Claude Desktop if you haven't already
2. Add the following configuration to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "freshdesk-mcp": {
    "command": "uvx",
    "args": [
        "freshdesk-mcp"
    ],
    "env": {
      "FRESHDESK_API_KEY": "<YOUR_FRESHDESK_API_KEY>",
      "FRESHDESK_DOMAIN": "<YOUR_FRESHDESK_DOMAIN>"
    }
  }
}
```

**Important Notes**:
- Replace `YOUR_FRESHDESK_API_KEY` with your actual Freshdesk API key
- Replace `YOUR_FRESHDESK_DOMAIN` with your Freshdesk domain (e.g., `yourcompany.freshdesk.com`)

## Example Operations

Once configured, you can ask Claude to perform operations like:

- "Create a new ticket with subject 'Payment Issue for customer A101' and description as 'Reaching out for a payment issue in the last month for customer A101', where customer email is a101@acme.com and set priority to high"
- "Update the status of ticket #12345 to 'Resolved'"
- "List all high-priority tickets assigned to the agent John Doe"
- "List previous tickets of customer A101 in last 30 days"

### Search Examples

- "Find all open tickets with high or urgent priority created after January 1st"
  ```python
  search_tickets("status:2 AND priority:>2 AND created_at:>'2023-01-01'")
  ```

- "Find tickets with tag 'billing' that are in pending status"
  ```python
  search_tickets("tag:'billing' AND status:3")
  ```

- "Find tickets with 'payment' mentioned in their subject or description"
  ```python
  search_tickets("payment")  # Free text search in subject and description
  ```

- "Find tickets created in the last month that have not been resolved"
  ```python
  # Using helper functions to build a more complex query
  unresolved = build_complex_search_query(
    build_search_query("status", 2),  # Open
    build_search_query("status", 3),  # Pending
    build_search_query("status", 6),  # Waiting on Customer
    operator="OR"
  )
  last_month = build_search_query("created_at", "2023-05-01", ">")  # Adjust date as needed

  # Combine the parts
  query = build_complex_search_query(unresolved, last_month, operator="AND")
  search_tickets(query)
  ```

## Testing

For testing purposes, you can start the server manually:

```bash
uvx freshdesk-mcp --env FRESHDESK_API_KEY=<your_api_key> --env FRESHDESK_DOMAIN=<your_domain>
```

## Troubleshooting

- Verify your Freshdesk API key and domain are correct
- Ensure proper network connectivity to Freshdesk servers
- Check API rate limits and quotas
- Verify the `uvx` command is available in your PATH
- For search query issues, use the helper functions or refer to the search syntax examples

## License

This MCP server is licensed under the MIT License. See the LICENSE file in the project repository for full details.
