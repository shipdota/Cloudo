import pytest
from unittest.mock import patch, MagicMock
from app.main import get_leaderboard_data, leaderboard_cache

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the leaderboard cache before each test."""
    leaderboard_cache.clear()

@patch('app.main.supabase')
def test_leaderboard_caching(mock_supabase, client):
    """Verify that leaderboard data is cached and Supabase is called only once."""

    # Mock data
    mock_data = [
        {'score': 100, 'created_at': '2023-01-01', 'profiles': {'username': 'Player1', 'avatar_url': ''}}
    ]

    # Setup mock chain
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

    # First call - should hit the database (mock)
    response1 = client.get('/leaderboard')
    assert response1.status_code == 200
    assert b"Player1" in response1.data

    # Verify Supabase was called
    mock_supabase.table.assert_called_once()

    # Reset mock call count to verify caching
    mock_supabase.table.reset_mock()

    # Second call - should use cache and NOT hit the database
    response2 = client.get('/leaderboard')
    assert response2.status_code == 200
    assert b"Player1" in response2.data

    # Verify Supabase was NOT called again
    mock_supabase.table.assert_not_called()
