import pytest
from unittest.mock import patch, MagicMock

@patch('app.main.supabase')
def test_leaderboard_caching(mock_supabase, client):
    # Mock data
    mock_data = [
        {'score': 100, 'created_at': '2023-01-01', 'profiles': {'username': 'Player1', 'avatar_url': ''}}
    ]

    # Mock the execute() result
    mock_execute = MagicMock()
    mock_execute.data = mock_data

    # Chain setup
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
    client.get('/leaderboard')

    # Second call
    client.get('/leaderboard')

    # Verify how many times the database was queried
    # Expected to be 1 (second call uses cache)

    # Check call count of supabase.table('scores')...
    assert mock_supabase.table.call_count == 1
