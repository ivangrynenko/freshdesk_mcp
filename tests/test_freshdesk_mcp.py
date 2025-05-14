import unittest
import asyncio
import os
from unittest.mock import patch, MagicMock
import httpx

from src.freshdesk_mcp.server import (
    create_ticket,
    get_ticket,
    update_ticket,
    delete_ticket,
    build_search_query,
    build_complex_search_query,
    search_tickets
)

class TestFreshdeskMCP(unittest.TestCase):
    # ... existing test methods ...

    # Search functionality tests
    def test_build_search_query_basic(self):
        """Test basic search query building"""
        # Test with string value
        self.assertEqual(
            build_search_query("type", "Question"),
            "type:'Question'"
        )

        # Test with numeric value
        self.assertEqual(
            build_search_query("status", 2),
            "status:2"
        )

        # Test with operator
        self.assertEqual(
            build_search_query("priority", 3, ">"),
            "priority:>3"
        )

    def test_build_complex_search_query_basic(self):
        """Test complex search query building"""
        # Test with multiple parts
        query1 = build_search_query("status", 2)
        query2 = build_search_query("priority", 3)

        # Test AND operator
        self.assertEqual(
            build_complex_search_query(query1, query2, operator="AND"),
            "(status:2 AND priority:3)"
        )

        # Test OR operator
        self.assertEqual(
            build_complex_search_query(query1, query2, operator="OR"),
            "(status:2 OR priority:3)"
        )

    @patch("httpx.AsyncClient")
    @unittest.skipIf(not os.environ.get("FRESHDESK_API_KEY"), "API key not set")
    def test_search_tickets(self, mock_client):
        """Test search_tickets functionality"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None

        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Run the async test
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_search_tickets(mock_client_instance))

    async def _test_search_tickets(self, mock_client):
        """Async helper for search_tickets test"""
        # Test basic search
        await search_tickets("status:2")

        # Verify the query was properly formatted
        mock_client.get.assert_called_with(
            'https://None/api/v2/search/tickets',
            headers={'Content-Type': 'application/json'},
            params={'query': '"status:2"'}
        )

        # Test free text search
        mock_client.reset_mock()
        await search_tickets("search term")

        # Verify it searches in description and subject
        self.assertTrue(
            '"(description:"search term" OR subject:"search term")"' in
            str(mock_client.get.call_args)
        )

if __name__ == '__main__':
    unittest.main()
