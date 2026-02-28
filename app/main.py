from flask import Blueprint, render_template, session, redirect, url_for
from threading import Lock
import time
from .db import supabase

main_bp = Blueprint('main', __name__)

# Cache leaderboard for 60 seconds to reduce DB queries
leaderboard_cache = {
    'data': None,
    'timestamp': 0
}
CACHE_TTL = 60
cache_lock = Lock()

def get_leaderboard_data():
    global leaderboard_cache
    current_time = time.time()

    with cache_lock:
        if leaderboard_cache['data'] is not None and (current_time - leaderboard_cache['timestamp']) < CACHE_TTL:
            return leaderboard_cache['data']

        # Fetch top 10 scores with user details
        # We don't catch exceptions here so that errors aren't cached for 60s
        response = supabase.table('scores') \
            .select('score, created_at, profiles(username, avatar_url)') \
            .order('score', desc=True) \
            .limit(10) \
            .execute()

        leaderboard_cache['data'] = response.data
        leaderboard_cache['timestamp'] = current_time
        return response.data

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    try:
        scores = get_leaderboard_data()
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        scores = []

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
