import time
import threading
from concurrent.futures import ThreadPoolExecutor
from flask import Blueprint, render_template, session, redirect, url_for, current_app
from .db import supabase

main_bp = Blueprint('main', __name__)

# Global cache for leaderboard to avoid DB hits on a read-heavy endpoint
_leaderboard_cache = {"data": None, "timestamp": 0}
_leaderboard_lock = threading.Lock()
LEADERBOARD_TTL = 60  # seconds

# Global thread pool for concurrent db queries (e.g., profile)
executor = ThreadPoolExecutor(max_workers=10)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    global _leaderboard_cache

    # Fast path: check cache validity without acquiring the lock
    current_time = time.time()
    if _leaderboard_cache["data"] is not None and current_time - _leaderboard_cache["timestamp"] < LEADERBOARD_TTL:
        scores = _leaderboard_cache["data"]
    else:
        with _leaderboard_lock:
            # Double-check inside the lock to prevent cache stampedes
            current_time = time.time()
            if _leaderboard_cache["data"] is not None and current_time - _leaderboard_cache["timestamp"] < LEADERBOARD_TTL:
                scores = _leaderboard_cache["data"]
            else:
                try:
                    # Fetch top 10 scores with user details
                    response = supabase.table('scores') \
                        .select('score, created_at, profiles(username, avatar_url)') \
                        .order('score', desc=True) \
                        .limit(10) \
                        .execute()

                    scores = response.data

                    # Update cache
                    _leaderboard_cache["data"] = scores
                    _leaderboard_cache["timestamp"] = time.time()
                except Exception as e:
                    scores = []
                    current_app.logger.error(f"Error fetching leaderboard: {e}")

    return render_template('leaderboard.html', scores=scores)

@main_bp.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user']['id']

    try:
        def fetch_profile():
            return supabase.table('profiles').select('*').eq('id', user_id).single().execute().data

        def fetch_scores():
            return supabase.table('scores') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('score', desc=True) \
                .limit(5) \
                .execute().data

        # Execute Supabase queries concurrently
        future_profile = executor.submit(fetch_profile)
        future_scores = executor.submit(fetch_scores)

        user_profile = future_profile.result()
        user_scores = future_scores.result()

    except Exception as e:
        user_profile = {}
        user_scores = []
        current_app.logger.error(f"Error fetching profile: {e}")

    return render_template('profile.html', profile=user_profile, scores=user_scores)
