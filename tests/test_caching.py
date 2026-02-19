import pytest
from unittest.mock import MagicMock, patch
from app.main import get_leaderboard_data, leaderboard_cache

def test_leaderboard_caching():
    # Clear cache before test to ensure clean state
    leaderboard_cache.clear()

    with patch('app.main.supabase') as mock_supabase:
        # Setup mock return
        mock_data = [{'score': 100, 'user': 'P1'}]
        mock_execute = MagicMock()
        mock_execute.data = mock_data

        # Chain setup: table -> select -> order -> limit -> execute
        mock_supabase.table.return_value \
            .select.return_value \
            .order.return_value \
            .limit.return_value \
            .execute.return_value = mock_execute

        # First call - should hit DB
        print("First call to get_leaderboard_data...")
        data1 = get_leaderboard_data()
        assert data1 == mock_data
        assert mock_supabase.table.call_count == 1
        print("First call verified: DB hit.")

        # Second call - should use cache, no DB hit
        print("Second call to get_leaderboard_data...")
        data2 = get_leaderboard_data()
        assert data2 == mock_data
        assert mock_supabase.table.call_count == 1 # Still 1
        print("Second call verified: Cache hit (no DB call).")

        # Verify cache content
        assert len(leaderboard_cache) == 1
