from flask import Blueprint, render_template, session, redirect, url_for, current_app
from .db import supabase
import threading
import time

main_bp = Blueprint('main', __name__)

# TTL Cache setup for leaderboard
LEADERBOARD_CACHE_TTL = 60 # 60 seconds
leaderboard_cache = {
    "data": [],
    "timestamp": 0
}
leaderboard_cache_lock = threading.Lock()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    global leaderboard_cache

    current_time = time.time()

    # Fast path: check if cache is valid
    if current_time - leaderboard_cache["timestamp"] < LEADERBOARD_CACHE_TTL:
        scores = leaderboard_cache["data"]
    else:
        # Slow path: cache is invalid, acquire lock
        with leaderboard_cache_lock:
            # Double-checked locking: check again inside the lock
            current_time = time.time() # Recalculate inside lock
            if current_time - leaderboard_cache["timestamp"] < LEADERBOARD_CACHE_TTL:
                scores = leaderboard_cache["data"]
            else:
                try:
                    # ⚡ Bolt Optimization: Cached expensive DB query for leaderboard
                    # Fetch top 10 scores with user details
                    response = supabase.table('scores') \
                        .select('score, created_at, profiles(username, avatar_url)') \
                        .order('score', desc=True) \
                        .limit(10) \
                        .execute()

                    scores = response.data

                    # Update cache
                    leaderboard_cache["data"] = scores
                    leaderboard_cache["timestamp"] = current_time
                except Exception as e:
                    scores = []
                    current_app.logger.error(f"Error fetching leaderboard: {e}")

    # Render outside of the lock
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
