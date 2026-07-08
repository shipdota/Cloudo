import time
import threading
from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase

main_bp = Blueprint('main', __name__)

_leaderboard_cache = {'data': None, 'timestamp': 0}
_leaderboard_lock = threading.Lock()
CACHE_TTL = 60  # Cache duration in seconds

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    current_time = time.time()

    # Fast path: check if cache is valid without locking
    if _leaderboard_cache['data'] is not None and current_time - _leaderboard_cache['timestamp'] < CACHE_TTL:
        scores = _leaderboard_cache['data']
    else:
        # Slow path: acquire lock to prevent cache stampedes
        with _leaderboard_lock:
            # Double check in case another thread updated the cache while we were waiting for the lock
            current_time = time.time()
            if _leaderboard_cache['data'] is not None and current_time - _leaderboard_cache['timestamp'] < CACHE_TTL:
                scores = _leaderboard_cache['data']
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
                    _leaderboard_cache['data'] = scores
                    _leaderboard_cache['timestamp'] = current_time
                except Exception as e:
                    # Fallback to cached data if possible, else empty list
                    scores = _leaderboard_cache['data'] or []
                    import logging
                    from flask import current_app
                    current_app.logger.error(f"Error fetching leaderboard: {e}")

    return render_template('leaderboard.html', scores=scores)

@main_bp.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user']['id']

    try:
        # Fetch profile
        profile_res = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
        user_profile = profile_res.data

        # Fetch user's recent top scores
        scores_res = supabase.table('scores') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('score', desc=True) \
            .limit(5) \
            .execute()

        user_scores = scores_res.data

    except Exception as e:
        user_profile = {}
        user_scores = []
        print(f"Error fetching profile: {e}")

    return render_template('profile.html', profile=user_profile, scores=user_scores)
