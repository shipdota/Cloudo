import time
import threading
from flask import Blueprint, render_template, session, redirect, url_for, current_app
from .db import supabase

main_bp = Blueprint('main', __name__)

# TTL Cache for leaderboard to prevent DB overload on read-heavy route
leaderboard_cache = {'data': None, 'timestamp': 0}
leaderboard_lock = threading.Lock()
CACHE_TTL = 60  # Cache duration in seconds

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    now = time.time()
    # Fast path: check if cache is valid
    if leaderboard_cache['data'] is not None and (now - leaderboard_cache['timestamp']) < CACHE_TTL:
        scores = leaderboard_cache['data']
    else:
        # Slow path: acquire lock to prevent cache stampedes
        with leaderboard_lock:
            # Double-check inside lock to ensure another thread hasn't just updated it
            now = time.time()
            if leaderboard_cache['data'] is not None and (now - leaderboard_cache['timestamp']) < CACHE_TTL:
                scores = leaderboard_cache['data']
            else:
                try:
                    # Fetch top 10 scores with user details
                    response = supabase.table('scores') \
                        .select('score, created_at, profiles(username, avatar_url)') \
                        .order('score', desc=True) \
                        .limit(10) \
                        .execute()

                    scores = response.data
                except Exception as e:
                    scores = []
                    current_app.logger.error(f"Error fetching leaderboard: {e}")

                # Update cache
                leaderboard_cache['data'] = scores
                leaderboard_cache['timestamp'] = now

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
