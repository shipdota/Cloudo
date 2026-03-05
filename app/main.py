from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase
import time
import threading

main_bp = Blueprint('main', __name__)

# Cache for leaderboard data to reduce DB load (60s TTL)
leaderboard_cache = {
    'data': [],
    'timestamp': 0
}
leaderboard_lock = threading.Lock()

def get_leaderboard_data():
    """Fetches leaderboard data, using a cache to minimize Supabase queries."""
    global leaderboard_cache

    with leaderboard_lock:
        current_time = time.time()
        # Return cached data if it's less than 60 seconds old
        if leaderboard_cache['data'] and (current_time - leaderboard_cache['timestamp'] < 60):
            return leaderboard_cache['data']

        try:
            # Fetch top 10 scores with user details
            response = supabase.table('scores') \
                .select('score, created_at, profiles(username, avatar_url)') \
                .order('score', desc=True) \
                .limit(10) \
                .execute()

            scores = response.data

            # Update cache
            leaderboard_cache['data'] = scores
            leaderboard_cache['timestamp'] = current_time

            return scores
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            # If fetch fails, try to return stale cache if available, otherwise empty list
            return leaderboard_cache['data'] if leaderboard_cache['data'] else []

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
