from flask import Blueprint, render_template, session, redirect, url_for
import time
import threading
from .db import supabase

main_bp = Blueprint('main', __name__)

leaderboard_cache = None
leaderboard_cache_time = 0
leaderboard_cache_lock = threading.Lock()

def get_leaderboard_data():
    global leaderboard_cache, leaderboard_cache_time
    current_time = time.time()

    with leaderboard_cache_lock:
        if leaderboard_cache is not None and (current_time - leaderboard_cache_time) < 60:
            return leaderboard_cache

        try:
            # Fetch top 10 scores with user details
            response = supabase.table('scores') \
                .select('score, created_at, profiles(username, avatar_url)') \
                .order('score', desc=True) \
                .limit(10) \
                .execute()

            leaderboard_cache = response.data
            leaderboard_cache_time = current_time
            return leaderboard_cache
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            if leaderboard_cache is not None:
                return leaderboard_cache
            return []

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    # Fetch cached top 10 scores
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
