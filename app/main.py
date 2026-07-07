import time
import threading
from flask import Blueprint, render_template, session, redirect, url_for, current_app
from .db import supabase

main_bp = Blueprint('main', __name__)

_leaderboard_cache = {'data': None, 'expires_at': 0}
_leaderboard_lock = threading.Lock()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    current_time = time.time()

    # Fast path: check cache validity without acquiring the lock
    if current_time < _leaderboard_cache['expires_at'] and _leaderboard_cache['data'] is not None:
        scores = _leaderboard_cache['data']
    else:
        with _leaderboard_lock:
            # Recalculate time and re-check cache inside lock to prevent stampedes
            current_time = time.time()
            if current_time < _leaderboard_cache['expires_at'] and _leaderboard_cache['data'] is not None:
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

                    # Update cache and set expiry (e.g., 60 seconds)
                    _leaderboard_cache['data'] = scores
                    _leaderboard_cache['expires_at'] = current_time + 60
                except Exception as e:
                    current_app.logger.error(f"Error fetching leaderboard: {e}")
                    # Fallback to empty list or existing cached data if any
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
