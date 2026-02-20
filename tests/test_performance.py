import pytest
from unittest.mock import patch, MagicMock
from app.main import leaderboard_cache

def test_leaderboard_caching(client):
    """Test that the leaderboard endpoint uses caching."""
    # Clear cache before test to ensure clean state
    leaderboard_cache.clear()

    # Mock the supabase response
    mock_data = [
        {'score': 100, 'created_at': '2023-01-01', 'profiles': {'username': 'Player1', 'avatar_url': ''}}
    ]
    mock_execute = MagicMock()
    mock_execute.data = mock_data

    # Setup chain: table -> select -> order -> limit -> execute
    with patch('app.main.supabase') as mock_supabase:
        mock_table = MagicMock()
        mock_select = MagicMock()
        mock_order = MagicMock()
        mock_limit = MagicMock()

        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.order.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.execute.return_value = mock_execute

        # First call: should hit the "database"
        response1 = client.get('/leaderboard')
        assert response1.status_code == 200
        assert b"Player1" in response1.data

        # Verify call count
        assert mock_supabase.table.call_count == 1, "Expected DB to be called once on first request"

        # Second call: should hit the cache
        response2 = client.get('/leaderboard')
        assert response2.status_code == 200
        assert b"Player1" in response2.data

        # Verify call count is still 1
        assert mock_supabase.table.call_count == 1, "Expected DB NOT to be called on second request (cached)"
