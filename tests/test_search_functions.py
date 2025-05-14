import asyncio
from freshdesk_mcp.server import search_tickets, build_search_query, build_complex_search_query

async def test_build_search_query():
    """Test the build_search_query function."""
    print("==== Testing build_search_query ====")

    # Test simple query with AND operator
    basic_query = await build_search_query([
        {"field": "status", "value": 2},
        {"field": "priority", "value": 3}
    ])
    print("Basic query (AND):", basic_query)

    # Test with OR operator
    or_query = await build_search_query([
        {"field": "status", "value": 2},
        {"field": "status", "value": 3}
    ], "OR")
    print("OR query:", or_query)

    # Test with string values
    string_query = await build_search_query([
        {"field": "tag", "value": "urgent"}
    ])
    print("String value query:", string_query)

    # Test with date comparator
    date_query = await build_search_query([
        {"field": "created_at", "value": "2023-01-01", "comparator": ":>"}
    ])
    print("Date query:", date_query)

    # Test with multiple conditions
    multi_query = await build_search_query([
        {"field": "status", "value": 2},
        {"field": "priority", "value": 3},
        {"field": "tag", "value": "important"}
    ])
    print("Multiple conditions query:", multi_query)

    # Test error handling for unsupported fields (should raise ValueError)
    try:
        invalid_query = await build_search_query([
            {"field": "subject", "value": "login"}
        ])
        print("ERROR: Should have failed with unsupported field")
    except ValueError as e:
        print(f"Correctly failed with unsupported field: {e}")

    # Test error handling for invalid operator
    try:
        invalid_op_query = await build_search_query([
            {"field": "status", "value": 2},
            {"field": "priority", "value": 3}
        ], "XOR")
        print("ERROR: Should have failed with invalid operator")
    except ValueError as e:
        print(f"Correctly failed with invalid operator: {e}")

async def test_build_complex_search_query():
    """Test the build_complex_search_query function."""
    print("\n==== Testing build_complex_search_query ====")

    # Test basic complex query
    complex_query = await build_complex_search_query([
        {
            "conditions": [
                {"field": "status", "value": 2},
                {"field": "priority", "value": 3}
            ],
            "operator": "AND"
        },
        {
            "conditions": [
                {"field": "tag", "value": "urgent"},
                {"field": "group", "value": 7}
            ],
            "operator": "OR"
        }
    ])
    print("Complex query:", complex_query)

    # Test with a single group
    single_group_query = await build_complex_search_query([
        {
            "conditions": [
                {"field": "status", "value": 2},
                {"field": "priority", "value": 3}
            ],
            "operator": "AND"
        }
    ])
    print("Single group query:", single_group_query)

    # Test with OR between groups
    or_groups_query = await build_complex_search_query([
        {
            "conditions": [
                {"field": "status", "value": 2}
            ],
            "operator": "AND"
        },
        {
            "conditions": [
                {"field": "status", "value": 3}
            ],
            "operator": "AND"
        }
    ], "OR")
    print("OR between groups query:", or_groups_query)

    # Test with empty conditions (should skip)
    empty_conditions_query = await build_complex_search_query([
        {
            "conditions": [
                {"field": "status", "value": 2}
            ],
            "operator": "AND"
        },
        {
            "conditions": [],
            "operator": "OR"
        }
    ])
    print("Query with empty conditions group:", empty_conditions_query)

async def test_search_tickets():
    """Test the search_tickets function (prints but doesn't execute actual API calls)."""
    print("\n==== Testing search_tickets (mock only) ====")

    # These are sample queries based on valid fields
    test_queries = [
        "tag:'Auth0'",
        "status:2",
        "priority:3 AND status:2",
        "created_at:>'2023-01-01'"
    ]

    for query in test_queries:
        print(f"Would execute search with query: {query}")

    # Build and use a query with the helper function
    query_result = await build_search_query([
        {"field": "status", "value": 2},
        {"field": "priority", "value": 3}
    ])
    print(f"Built query: {query_result['query']}")
    print(f"Would execute search with built query: {query_result['query']}")

async def main():
    """Run all the test functions."""
    await test_build_search_query()
    await test_build_complex_search_query()
    await test_search_tickets()

if __name__ == "__main__":
    asyncio.run(main())
