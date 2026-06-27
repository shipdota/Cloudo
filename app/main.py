from flask import Blueprint, render_template, session, redirect, url_for, current_app
from .db import supabase
import threading
import time

main_bp = Blueprint('main', __name__)

# TTL Cache for leaderboard
_leaderboard_cache = {'data': None, 'expires_at': 0}
_leaderboard_lock = threading.Lock()
LEADERBOARD_TTL_SECONDS = 30

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    current_time = time.time()

    # Fast path check
    if _leaderboard_cache['data'] is not None and current_time < _leaderboard_cache['expires_at']:
        return render_template('leaderboard.html', scores=_leaderboard_cache['data'])

    with _leaderboard_lock:
        current_time = time.time() # Recalculate inside lock
        if _leaderboard_cache['data'] is None or current_time >= _leaderboard_cache['expires_at']:
            try:
                # Fetch top 10 scores with user details
                response = supabase.table('scores') \
                    .select('score, created_at, profiles(username, avatar_url)') \
                    .order('score', desc=True) \
                    .limit(10) \
                    .execute()

                _leaderboard_cache['data'] = response.data
                _leaderboard_cache['expires_at'] = current_time + LEADERBOARD_TTL_SECONDS
            except Exception as e:
                current_app.logger.error(f"Error fetching leaderboard: {e}")
                # Ensure we have a default to prevent template errors
                _leaderboard_cache['data'] = _leaderboard_cache['data'] or []

        scores = _leaderboard_cache['data']

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
        current_app.logger.error(f"Error fetching profile: {e}")

    return render_template('profile.html', profile=user_profile, scores=user_scores)
