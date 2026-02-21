import pytest
from unittest.mock import patch, MagicMock
from app.main import leaderboard_cache

@patch('app.main.supabase')
def test_leaderboard_caching(mock_supabase, client):
    # Clear cache before test to ensure clean state
    leaderboard_cache.clear()

    # Mock data
    mock_data = [
        {'score': 100, 'created_at': '2023-01-01', 'profiles': {'username': 'Player1', 'avatar_url': ''}}
    ]

    # Setup the mocks
    mock_execute = MagicMock()
    mock_execute.data = mock_data

    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_order = MagicMock()
    mock_limit = MagicMock()

    mock_supabase.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.order.return_value = mock_order
    mock_order.limit.return_value = mock_limit
    mock_limit.execute.return_value = mock_execute

    # First call
    response1 = client.get('/leaderboard')
    assert response1.status_code == 200
    assert b"Player1" in response1.data

    # Assert that the database query was made
    # Note: Depending on implementation, table() might be called multiple times if chaining is done differently,
    # but here we expect at least one call. Let's verify call count matches expectations.
    assert mock_supabase.table.call_count == 1

    # Second call
    response2 = client.get('/leaderboard')
    assert response2.status_code == 200
    assert b"Player1" in response2.data

    # Assert that the database query was NOT made again (call count remains 1)
    assert mock_supabase.table.call_count == 1
