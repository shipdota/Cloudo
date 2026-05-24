from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase
import time
import threading

main_bp = Blueprint('main', __name__)

# Cache configuration for the leaderboard
LEADERBOARD_CACHE_TTL = 60  # seconds
_leaderboard_cache = None
_leaderboard_cache_time = 0
_leaderboard_lock = threading.Lock()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    global _leaderboard_cache, _leaderboard_cache_time

    current_time = time.time()

    # Fast path: check if cache is valid without lock
    if _leaderboard_cache is not None and (current_time - _leaderboard_cache_time) < LEADERBOARD_CACHE_TTL:
        scores = _leaderboard_cache
    else:
        with _leaderboard_lock:
            # Double-checked locking pattern inside the lock
            current_time = time.time()
            if _leaderboard_cache is None or (current_time - _leaderboard_cache_time) >= LEADERBOARD_CACHE_TTL:
                try:
                    # Fetch top 10 scores with user details
                    response = supabase.table('scores') \
                        .select('score, created_at, profiles(username, avatar_url)') \
                        .order('score', desc=True) \
                        .limit(10) \
                        .execute()

                    _leaderboard_cache = response.data
                    _leaderboard_cache_time = time.time()
                except Exception as e:
                    print(f"Error fetching leaderboard: {e}")
                    if _leaderboard_cache is None:
                        _leaderboard_cache = []

            scores = _leaderboard_cache

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
