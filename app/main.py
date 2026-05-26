from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase
import time
import threading

main_bp = Blueprint('main', __name__)

# Leaderboard Cache
LEADERBOARD_CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 60  # seconds
cache_lock = threading.Lock()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    now = time.time()

    # Fast path: check if cache is valid without locking
    if LEADERBOARD_CACHE["data"] is not None and (now - LEADERBOARD_CACHE["timestamp"]) < CACHE_TTL:
        scores = LEADERBOARD_CACHE["data"]
    else:
        # Slow path: acquire lock to update cache
        with cache_lock:
            # Recalculate 'now' inside the lock to avoid race conditions
            now_inside_lock = time.time()
            # Double-checked locking: check again in case another thread already updated it
            if LEADERBOARD_CACHE["data"] is not None and (now_inside_lock - LEADERBOARD_CACHE["timestamp"]) < CACHE_TTL:
                scores = LEADERBOARD_CACHE["data"]
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
                    LEADERBOARD_CACHE["data"] = scores
                    LEADERBOARD_CACHE["timestamp"] = now_inside_lock
                except Exception as e:
                    scores = LEADERBOARD_CACHE["data"] if LEADERBOARD_CACHE["data"] is not None else []
                    print(f"Error fetching leaderboard: {e}")

    # Render template outside of the lock to minimize lock duration
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
