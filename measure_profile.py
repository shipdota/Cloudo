import time
import sys
from unittest.mock import MagicMock

sys.modules['flask'] = MagicMock()
import app.main
from app.main import main_bp

# Mock the supabase client
mock_supabase = MagicMock()
app.main.supabase = mock_supabase

def mock_execute(*args, **kwargs):
    time.sleep(0.1) # Simulate 100ms network latency
    res = MagicMock()
    res.data = {}
    return res

mock_supabase.table().select().eq().single().execute = mock_execute
mock_supabase.table().select().eq().order().limit().execute = mock_execute

# Sequential version
def profile_sequential():
    user_id = 1
    start = time.time()
    profile_res = mock_supabase.table('profiles').select('*').eq('id', user_id).single().execute()
    scores_res = mock_supabase.table('scores').select('*').eq('user_id', user_id).order('score', desc=True).limit(5).execute()
    print(f"Sequential: {time.time() - start:.3f}s")

# Parallel version
import concurrent.futures
def profile_parallel():
    user_id = 1
    start = time.time()

    def fetch_profile():
        return mock_supabase.table('profiles').select('*').eq('id', user_id).single().execute()

    def fetch_scores():
        return mock_supabase.table('scores').select('*').eq('user_id', user_id).order('score', desc=True).limit(5).execute()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(fetch_profile)
        f2 = executor.submit(fetch_scores)
        f1.result()
        f2.result()

    print(f"Parallel: {time.time() - start:.3f}s")

profile_sequential()
profile_parallel()
