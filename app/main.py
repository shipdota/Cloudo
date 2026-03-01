import time
import threading
from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase

main_bp = Blueprint('main', __name__)

leaderboard_cache = {}
cache_lock = threading.Lock()

def get_leaderboard_data():
    """Fetch leaderboard data with a 60-second TTL cache."""
    current_time = time.time()

    with cache_lock:
        if 'data' in leaderboard_cache and current_time - leaderboard_cache.get('timestamp', 0) < 60:
            return leaderboard_cache['data']

    try:
        # Fetch top 10 scores with user details
        response = supabase.table('scores') \
            .select('score, created_at, profiles(username, avatar_url)') \
            .order('score', desc=True) \
            .limit(10) \
            .execute()

        scores = response.data

        with cache_lock:
            leaderboard_cache['data'] = scores
            leaderboard_cache['timestamp'] = current_time

    except Exception as e:
        scores = []
        print(f"Error fetching leaderboard: {e}")

    return scores

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
