from flask import Blueprint, render_template, session, redirect, url_for
import time
import threading
from .db import supabase

main_bp = Blueprint('main', __name__)

# ⚡ Bolt: Caching leaderboard to prevent identical DB calls on every load
leaderboard_cache = {"data": None, "timestamp": 0}
cache_lock = threading.Lock()

def get_leaderboard_data():
    """Fetch leaderboard data with a 60-second TTL cache."""
    global leaderboard_cache

    with cache_lock:
        current_time = time.time()
        # Return cached data if valid (60s TTL)
        if leaderboard_cache["data"] is not None and (current_time - leaderboard_cache["timestamp"]) < 60:
            return leaderboard_cache["data"]

    # If cache is missed or expired, fetch from DB
    try:
        response = supabase.table('scores') \
            .select('score, created_at, profiles(username, avatar_url)') \
            .order('score', desc=True) \
            .limit(10) \
            .execute()
        data = response.data
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        # Return previous cached data if DB fails, or empty list
        with cache_lock:
            return leaderboard_cache["data"] if leaderboard_cache["data"] is not None else []

    # Update cache
    with cache_lock:
        leaderboard_cache["data"] = data
        leaderboard_cache["timestamp"] = time.time()

    return data

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    scores = get_leaderboard_data()
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
