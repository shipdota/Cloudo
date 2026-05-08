from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase
import time
import threading

main_bp = Blueprint('main', __name__)

# TTL Cache for leaderboard to prevent database overload
# 60 seconds TTL as leaderboard doesn't need to be real-time
CACHE_TTL = 60
leaderboard_cache = {
    'data': None,
    'timestamp': 0
}
cache_lock = threading.Lock()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    current_time = time.time()

    scores = None

    # Fast path: Read from cache with minimal locking if it's fresh
    # We only lock around the read check to minimize contention
    with cache_lock:
        is_cache_valid = leaderboard_cache['data'] is not None and (current_time - leaderboard_cache['timestamp']) < CACHE_TTL
        if is_cache_valid:
            scores = leaderboard_cache['data']

    if scores is not None:
        return render_template('leaderboard.html', scores=scores)

    # Cache miss or expired. Acquire lock to update.
    with cache_lock:
        # Double-check inside lock to prevent cache stampede
        current_time = time.time()
        is_cache_valid = leaderboard_cache['data'] is not None and (current_time - leaderboard_cache['timestamp']) < CACHE_TTL
        if is_cache_valid:
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

                # Update cache inside lock
                leaderboard_cache['data'] = scores
                leaderboard_cache['timestamp'] = time.time()

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
