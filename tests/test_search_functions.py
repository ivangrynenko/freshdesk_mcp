import asyncio
from freshdesk_mcp.server import search_tickets, build_search_query, build_complex_search_query
import unittest
import os
import pytest
from unittest.mock import patch, MagicMock
import httpx

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

    # Test with company_id
    company_query = await build_search_query([
        {"field": "company_id", "value": 51000627082}
    ])
    print("Company ID query:", company_query)

    # Test with agent_id
    agent_query = await build_search_query([
        {"field": "agent_id", "value": 123456}
    ])
    print("Agent ID query:", agent_query)

    # Test with custom field
    custom_field_query = await build_search_query([
        {"field": "cf_department", "value": "IT"}
    ])
    print("Custom field query:", custom_field_query)

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
                {"field": "company_id", "value": 51000627082}
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
                {"field": "agent_id", "value": 123456}
            ],
            "operator": "AND"
        },
        {
            "conditions": [
                {"field": "group_id", "value": 7890}
            ],
            "operator": "AND"
        }
    ], "OR")
    print("OR between groups query:", or_groups_query)

    # Test with custom fields
    custom_field_query = await build_complex_search_query([
        {
            "conditions": [
                {"field": "cf_department", "value": "IT"},
                {"field": "status", "value": 2}
            ],
            "operator": "AND"
        }
    ])
    print("Custom field query:", custom_field_query)

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
        "created_at:>'2023-01-01'",
        "company_id:51000627082",
        "agent_id:123456",
        "cf_department:'IT'"
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

    # Complex query example
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
                {"field": "company_id", "value": 51000627082}
            ],
            "operator": "OR"
        }
    ])
    print(f"Built complex query: {complex_query['query']}")
    print(f"Would execute search with complex query: {complex_query['query']}")

class TestSearchFunctions(unittest.TestCase):
    """Tests for Freshdesk search-related functions"""

    def test_build_search_query_string(self):
        """Test build_search_query with string values"""
        # Test with string value (should add single quotes)
        result = build_search_query("type", "Question")
        self.assertEqual(result, "type:'Question'")

        # Test with string value and comparison operator
        result = build_search_query("created_at", "2023-01-01", ">")
        self.assertEqual(result, "created_at:>'2023-01-01'")

    def test_build_search_query_numeric(self):
        """Test build_search_query with numeric values"""
        # Test with numeric value (no quotes)
        result = build_search_query("status", 2)
        self.assertEqual(result, "status:2")

        # Test with numeric value and comparison operator
        result = build_search_query("priority", 3, ">")
        self.assertEqual(result, "priority:>3")

    def test_build_search_query_boolean(self):
        """Test build_search_query with boolean values"""
        # Test with boolean value
        result = build_search_query("cf_verified", True)
        self.assertEqual(result, "cf_verified:True")

        result = build_search_query("cf_active", False)
        self.assertEqual(result, "cf_active:False")

    def test_build_search_query_null(self):
        """Test build_search_query with None values"""
        # Test with None value (should become null)
        result = build_search_query("agent_id", None)
        self.assertEqual(result, "agent_id:null")

    def test_build_complex_search_query_single(self):
        """Test build_complex_search_query with a single part"""
        # Test with a single part (should not add parentheses)
        part = build_search_query("status", 2)
        result = build_complex_search_query(part)
        self.assertEqual(result, "status:2")

    def test_build_complex_search_query_multiple(self):
        """Test build_complex_search_query with multiple parts"""
        # Test with multiple parts using AND
        part1 = build_search_query("status", 2)
        part2 = build_search_query("priority", 3)
        result = build_complex_search_query(part1, part2, operator="AND")
        self.assertEqual(result, "(status:2 AND priority:3)")

        # Test with multiple parts using OR
        result = build_complex_search_query(part1, part2, operator="OR")
        self.assertEqual(result, "(status:2 OR priority:3)")

    def test_build_complex_search_query_nested(self):
        """Test build_complex_search_query with nested complex queries"""
        # Test with nested complex queries
        status_open = build_search_query("status", 2)
        status_pending = build_search_query("status", 3)
        statuses = build_complex_search_query(status_open, status_pending, operator="OR")

        priority_high = build_search_query("priority", 3)
        priority_urgent = build_search_query("priority", 4)
        priorities = build_complex_search_query(priority_high, priority_urgent, operator="OR")

        result = build_complex_search_query(statuses, priorities, operator="AND")
        self.assertEqual(result, "((status:2 OR status:3) AND (priority:3 OR priority:4))")

    @patch("httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_search_tickets_format(self, mock_client):
        """Test that search_tickets properly formats the query"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Test with already properly formatted query
        await search_tickets('"status:2"')

        # Verify the query was passed correctly
        mock_client_instance.get.assert_called_with(
            'https://None/api/v2/search/tickets',
            headers={'Content-Type': 'application/json'},
            params={'query': '"status:2"'}
        )

        # Reset mock
        mock_client_instance.reset_mock()

        # Test with unquoted query - should add quotes
        await search_tickets('status:2')

        # Verify quotes were added
        mock_client_instance.get.assert_called_with(
            'https://None/api/v2/search/tickets',
            headers={'Content-Type': 'application/json'},
            params={'query': '"status:2"'}
        )

    @patch("httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_search_tickets_free_text(self, mock_client):
        """Test that search_tickets handles free text queries"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Test with free text query (no field:value format)
        await search_tickets('payment issue')

        # Verify it was converted to search in description and subject
        mock_client_instance.get.assert_called_with(
            'https://None/api/v2/search/tickets',
            headers={'Content-Type': 'application/json'},
            params={'query': '"(description:"payment issue" OR subject:"payment issue")"'}
        )

    @patch("httpx.AsyncClient")
    @pytest.mark.asyncio
    async def test_search_tickets_error_handling(self, mock_client):
        """Test that search_tickets properly handles errors"""
        # Setup mock error response
        mock_error = httpx.HTTPStatusError(
            "Client error '400 Bad Request'",
            request=MagicMock(),
            response=MagicMock()
        )
        mock_error.response.status_code = 400
        mock_error.response.json.return_value = {
            "description": "Validation failed",
            "errors": [
                {
                    "field": "query",
                    "message": "Given query is invalid",
                    "code": "invalid_value"
                }
            ]
        }

        mock_client_instance = MagicMock()
        mock_client_instance.get.side_effect = mock_error
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Test error handling
        result = await search_tickets('invalid:query')

        # Verify it includes the error details
        self.assertIn("error", result)
        self.assertIn("details", result)
        self.assertIn("query_sent", result)
        self.assertEqual(result["query_sent"], '"invalid:query"')

async def main():
    """Run all the test functions."""
    await test_build_search_query()
    await test_build_complex_search_query()
    await test_search_tickets()

if __name__ == "__main__":
    unittest.main()
