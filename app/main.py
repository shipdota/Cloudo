from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase
import time
import threading

main_bp = Blueprint('main', __name__)

# Cache for leaderboard
LEADERBOARD_CACHE = {'data': None, 'timestamp': 0}
CACHE_TTL = 60  # 60 seconds TTL
leaderboard_lock = threading.Lock()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    current_time = time.time()

    # Fast path: check if cache is valid
    if LEADERBOARD_CACHE['data'] is not None and (current_time - LEADERBOARD_CACHE['timestamp']) < CACHE_TTL:
        scores = LEADERBOARD_CACHE['data']
    else:
        # Slow path: acquire lock and fetch
        with leaderboard_lock:
            # Double check inside the lock
            current_time = time.time()
            if LEADERBOARD_CACHE['data'] is not None and (current_time - LEADERBOARD_CACHE['timestamp']) < CACHE_TTL:
                scores = LEADERBOARD_CACHE['data']
            else:
                try:
                    # Fetch top 10 scores with user details
                    response = supabase.table('scores') \
                        .select('score, created_at, profiles(username, avatar_url)') \
                        .order('score', desc=True) \
                        .limit(10) \
                        .execute()

                    scores = response.data

                    # Update cache
                    LEADERBOARD_CACHE['data'] = scores
                    LEADERBOARD_CACHE['timestamp'] = current_time
                except Exception as e:
                    scores = []
                    print(f"Error fetching leaderboard: {e}")

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
