import asyncio
from freshdesk_mcp.server import get_ticket, update_ticket, get_ticket_conversation, update_ticket_conversation,get_agents, list_canned_responses, list_solution_articles, list_solution_categories,list_solution_folders,list_groups,create_group,create_contact_field,create_canned_response_folder,update_canned_response_folder,create_canned_response,update_canned_response,view_canned_response, search_tickets, build_search_query, build_complex_search_query

async def test_get_ticket():
    ticket_id = "1289" #Replace with a test ticket Id
    result = await get_ticket(ticket_id)
    print(result)


async def test_update_ticket():
    ticket_id = 1289 #Replace with a test ticket Id
    ticket_fields = {"status": 5}
    result = await update_ticket(ticket_id, ticket_fields)
    print(result)

async def test_get_ticket_conversation():
    ticket_id = 1294 #Replace with a test ticket Id
    result = await get_ticket_conversation(ticket_id)
    print(result)

async def test_update_ticket_conversation():
    conversation_id = 60241927935 #Replace with a test conversation Id
    body = "This is a test reply"
    result = await update_ticket_conversation(conversation_id, body)
    print(result)

async def test_get_agents():
    page = 1
    per_page = 30
    result = await get_agents(page, per_page)
    print(result)

async def test_list_canned_responses():
    result = await list_canned_responses()
    print(result)

async def test_list_solution_articles():
    result = await list_solution_articles()
    print(result)

async def test_list_solution_folders():
    category_id = 60000237037
    result = await list_solution_folders(category_id)
    print(result)

async def test_list_solution_categories():
    result = await list_solution_categories()
    print(result)

async def test_list_solution_articles():
    folder_id = 60000347598
    result = await list_solution_articles(folder_id)
    print(result)

async def test_list_groups():
    result = await list_groups()
    print(result)
async def test_create_group():
    group_fields = {

    }
    result = await create_group(group_fields)
    print(result)
async def test_create_contact_field():
    contact_field_fields = {
        "label": "Robot Humor Processor",
        "label_for_customers": "Robot Humor Processor",
        "type": "custom_dropdown",
        "description": "Measures how well this contact understands AI jokes",
        "required_for_agents": False,
        "displayed_for_customers": True,
        "customers_can_edit": True,
        "choices": [{"value":"Still rebooting brain.exe","position":1},
            {"value":"Laughs in binary","position":2},
            {"value":"Dad jokes only","position":3},
            {"value":"Gets AI humor 404: Not Found","position":4},
            {"value":"Certified AI Comedian","position":5},
            {"value":"Makes ChatGPT snort-laugh","position":6},
            {"value":"Could teach HAL 9000 to smile","position":7}
            ],
        "position":1
    }
    result = await create_contact_field(contact_field_fields)
    print(result)
async def test_create_canned_response_folder():
    name = "Test Folder"
    result = await create_canned_response_folder(name)
    print(result)
async def test_update_canned_response_folder():
    folder_id = 60000074861
    name = "Test Folder1"
    result = await update_canned_response_folder(folder_id, name)
    print(result)
async def test_create_canned_response():
    canned_response_fields = {
        "title": "Test Canned Response 2",
        "name": "Test Canned Response 2",
        "description": "This is a test canned response",
        "folder_id": 60000074861,
        "content_html": "This is a test canned response",
        "visibility": "1"
    }
    result = await create_canned_response(canned_response_fields)
    print(result)
async def test_update_canned_response():
    canned_response_id = 60000168320
    canned_response_fields = {
        "title": "Test Canned Response 5",
        "folder_id": 60000103470,
        "content_html": "This is a test canned response",
        "visibility": 1
    }
    result = await update_canned_response(canned_response_id, canned_response_fields)
    print(result)
async def test_view_canned_response():
    canned_response_id = 60000168320
    result = await view_canned_response(canned_response_id)
    print(result)

# New search functionality tests
async def test_search_tickets_basic():
    query = "status:2"  # Open tickets
    result = await search_tickets(query)
    print(f"Search results for '{query}':")
    print(result)

async def test_build_and_search():
    # Build a query for high priority open tickets
    query_data = await build_search_query([
        {"field": "status", "value": 2},
        {"field": "priority", "value": 3}
    ])
    query = query_data.get("query")
    print(f"Built query: {query}")

    # Use the built query to search
    result = await search_tickets(query)
    print(f"Search results:")
    print(result)

async def test_complex_search():
    # Build a complex query for (open OR pending) AND (high OR urgent)
    query_data = await build_complex_search_query([
        {
            "conditions": [
                {"field": "status", "value": 2},  # Open
                {"field": "status", "value": 3}   # Pending
            ],
            "operator": "OR"
        },
        {
            "conditions": [
                {"field": "priority", "value": 3},  # High
                {"field": "priority", "value": 4}   # Urgent
            ],
            "operator": "OR"
        }
    ])
    query = query_data.get("query")
    print(f"Built complex query: {query}")

    # Use the built query to search
    result = await search_tickets(query)
    print(f"Complex search results:")
    print(result)

if __name__ == "__main__":
    # asyncio.run(test_get_ticket())
    # asyncio.run(test_update_ticket())
    # asyncio.run(test_get_ticket_conversation())
    # asyncio.run(test_update_ticket_conversation())
    # asyncio.run(test_get_agents())
    # asyncio.run(test_list_canned_responses())
    # asyncio.run(test_list_solution_articles())
    # asyncio.run(test_list_solution_folders())
    # asyncio.run(test_list_solution_categories())
    # asyncio.run(test_list_groups())
    # asyncio.run(test_create_canned_response_folder())
    # asyncio.run(test_update_canned_response_folder())
    # asyncio.run(test_create_canned_response())
    # asyncio.run(test_view_canned_response())
    # asyncio.run(test_update_canned_response())

    # Uncomment to test search functionality
    # asyncio.run(test_search_tickets_basic())
    # asyncio.run(test_build_and_search())
    asyncio.run(test_complex_search())
