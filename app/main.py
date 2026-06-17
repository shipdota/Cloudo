from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase
import time
import threading

main_bp = Blueprint('main', __name__)

# Cache for leaderboard to reduce database queries
# Leaderboard changes frequently but doesn't need to be real-time
_leaderboard_cache = {
    'data': None,
    'expires_at': 0
}
_leaderboard_lock = threading.Lock()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    current_time = time.time()

    # Fast path: Check if cache is valid without locking
    if _leaderboard_cache['data'] is not None and current_time < _leaderboard_cache['expires_at']:
        scores = _leaderboard_cache['data']
    else:
        # Slow path: Cache is invalid or missing, acquire lock
        with _leaderboard_lock:
            # Double-check inside lock in case another thread already updated it
            current_time = time.time()
            if _leaderboard_cache['data'] is not None and current_time < _leaderboard_cache['expires_at']:
                scores = _leaderboard_cache['data']
            else:
                try:
                    # Fetch top 10 scores with user details
                    response = supabase.table('scores') \
                        .select('score, created_at, profiles(username, avatar_url)') \
                        .order('score', desc=True) \
                        .limit(10) \
                        .execute()

                    # Update cache (TTL 30 seconds)
                    _leaderboard_cache['data'] = response.data
                    _leaderboard_cache['expires_at'] = current_time + 30
                except Exception as e:
                    print(f"Error fetching leaderboard: {e}")
                    # If fetch fails, keep old cache if available to prevent showing empty board
                    if _leaderboard_cache['data'] is None:
                        _leaderboard_cache['data'] = []

                scores = _leaderboard_cache['data'] or []

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
