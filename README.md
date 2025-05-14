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

#### Valid Search Fields

Freshdesk ticket search API supports only a limited set of search fields:

- `tag`: Search by ticket tags
- `status`: Ticket status (e.g., 2=Open, 3=Pending, 4=Resolved, 5=Closed)
- `priority`: Ticket priority (1=Low, 2=Medium, 3=High, 4=Urgent)
- `type`: Type of the ticket (e.g., Problem, Question, etc.)
- `requester`: Email of the requester
- `responder`: Agent assigned to the ticket
- `group`: Group assigned to the ticket
- `due_by`: Due date of the ticket
- `created_at`: Ticket creation date
- `updated_at`: Ticket last updated date
- `fr_due_by`: First response due by date
- `created_date`: Alternative for created_at
- `updated_date`: Alternative for updated_at
- `notes`: Search in ticket notes
- `description`: Search in ticket description

#### Search Helper Functions

For convenient search query construction, the following helper functions are provided:

- `build_search_query`: Constructs a valid Freshdesk search query from a list of condition dictionaries
- `build_complex_search_query`: Constructs complex search queries with nested condition groups

#### Example Usage

```python
# Simple search for open tickets
search_tickets("status:2")

# Search for high priority open tickets
search_tickets("priority:3 AND status:2")

# Search for tickets with a specific tag
search_tickets("tag:'urgent'")

# Using the helper function to build a query
query_result = await build_search_query([
    {"field": "status", "value": 2},
    {"field": "priority", "value": 3}
])
search_result = await search_tickets(query_result["query"])
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
- "Find all open tickets with high or urgent priority created after January 1st" (using the new search functionality)
- "Search for tickets with the tag 'billing' that are in pending status"

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
