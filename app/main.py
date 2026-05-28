from flask import Blueprint, render_template, session, redirect, url_for
import time
import threading
from .db import supabase

main_bp = Blueprint('main', __name__)

# Cache for the leaderboard to reduce database queries
# Format: {'data': [...], 'expires_at': timestamp}
leaderboard_cache = {'data': [], 'expires_at': 0}
leaderboard_cache_lock = threading.Lock()
CACHE_TTL_SECONDS = 60

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    current_time = time.time()

    # Fast path: Check if cache is valid (without locking)
    if current_time < leaderboard_cache['expires_at'] and leaderboard_cache['data']:
        scores = leaderboard_cache['data']
    else:
        # Cache is invalid or empty, acquire lock
        with leaderboard_cache_lock:
            # Double-checked locking: check again in case another thread updated it
            current_time = time.time()
            if current_time < leaderboard_cache['expires_at'] and leaderboard_cache['data']:
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

                    # Update cache
                    leaderboard_cache['data'] = scores
                    leaderboard_cache['expires_at'] = current_time + CACHE_TTL_SECONDS
                except Exception as e:
                    # If fetch fails, use stale cache if available, otherwise empty list
                    scores = leaderboard_cache['data'] if leaderboard_cache['data'] else []
                    print(f"Error fetching leaderboard: {e}")

    # Render outside the lock to minimize contention
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
