import pytest
import time
from unittest.mock import patch, MagicMock

@pytest.mark.benchmark
@patch('app.main.supabase')
def test_leaderboard_performance(mock_supabase, client):
    # Mock data
    mock_data = [
        {'score': 100, 'created_at': '2023-01-01', 'profiles': {'username': 'Player1', 'avatar_url': ''}},
        {'score': 50, 'created_at': '2023-01-02', 'profiles': {'username': 'Player2', 'avatar_url': ''}}
    ]

    # Setup mock with delay
    def delayed_execute(*args, **kwargs):
        time.sleep(0.1)  # Simulate 100ms DB latency
        mock_execute = MagicMock()
        mock_execute.data = mock_data
        return mock_execute

    # Create the chain of mocks
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_order = MagicMock()
    mock_limit = MagicMock()

    mock_supabase.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.order.return_value = mock_order
    mock_order.limit.return_value = mock_limit
    mock_limit.execute.side_effect = delayed_execute

    start_time = time.time()

    # Make 5 requests
    # With caching, the first request takes ~0.1s, subsequent ones take ~0s
    for _ in range(5):
        response = client.get('/leaderboard')
        assert response.status_code == 200
        assert b"Player1" in response.data

    end_time = time.time()
    duration = end_time - start_time

    print(f"\nTime taken for 5 requests: {duration:.4f}s")

    # Assert that caching is working.
    # Without caching: 5 * 0.1s = 0.5s
    # With caching: 1 * 0.1s + overhead = ~0.1s + overhead
    assert duration < 0.25, f"Expected duration < 0.25s (caching active), but got {duration:.4f}s"
