from flask import Blueprint, render_template, session, redirect, url_for, current_app
from .db import supabase
import time
import threading
import concurrent.futures

main_bp = Blueprint('main', __name__)

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

_leaderboard_cache = {'data': None, 'expires_at': 0}
_leaderboard_lock = threading.Lock()
CACHE_TTL = 60  # seconds

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    """Display the top 10 scores on the leaderboard with a TTL cache to prevent database overload."""
    now = time.time()

    # Fast path: check if cache is valid without locking
    if _leaderboard_cache['data'] is not None and now < _leaderboard_cache['expires_at']:
        scores = _leaderboard_cache['data']
    else:
        # Slow path: acquire lock to update cache
        with _leaderboard_lock:
            # Recalculate time inside lock to prevent cache stampedes and race conditions
            now = time.time()
            if _leaderboard_cache['data'] is None or now >= _leaderboard_cache['expires_at']:
                try:
                    # Fetch top 10 scores with user details
                    response = supabase.table('scores') \
                        .select('score, created_at, profiles(username, avatar_url)') \
                        .order('score', desc=True) \
                        .limit(10) \
                        .execute()

                    _leaderboard_cache['data'] = response.data
                    _leaderboard_cache['expires_at'] = now + CACHE_TTL
                except Exception as e:
                    current_app.logger.error(f"Error fetching leaderboard: {e}")

            # Ensure safe fallback type if initial fetch failed
            scores = _leaderboard_cache['data'] or []

    # Expensive operation rendered outside the lock
    return render_template('leaderboard.html', scores=scores)

@main_bp.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user']['id']

    try:
        # Define functions for concurrent execution
        def fetch_profile():
            return supabase.table('profiles').select('*').eq('id', user_id).single().execute()

        def fetch_scores():
            return supabase.table('scores') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('score', desc=True) \
                .limit(5) \
                .execute()

        # Submit tasks to the executor
        profile_future = _executor.submit(fetch_profile)
        scores_future = _executor.submit(fetch_scores)

        # Wait for results concurrently
        user_profile = profile_future.result().data
        user_scores = scores_future.result().data

    except Exception as e:
        user_profile = {}
        user_scores = []
        current_app.logger.error(f"Error fetching profile: {e}")

    return render_template('profile.html', profile=user_profile, scores=user_scores)
