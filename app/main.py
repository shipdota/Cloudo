from flask import Blueprint, render_template, session, redirect, url_for, current_app
from .db import supabase
import time
import threading

main_bp = Blueprint('main', __name__)

# ⚡ Bolt Optimization: Thread-safe TTL Cache
# 💡 What: In-memory cache for the leaderboard endpoint with a 60-second TTL.
# 🎯 Why: Prevents expensive network/database calls to Supabase on every single page load for this read-heavy route.
# 📊 Impact: Significantly speeds up response times and reduces database load under high traffic.
leaderboard_cache = {'data': None, 'timestamp': 0}
cache_lock = threading.Lock()
CACHE_TTL = 60

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    current_time = time.time()

    scores = None

    with cache_lock:
        if leaderboard_cache['data'] is not None and (current_time - leaderboard_cache['timestamp']) < CACHE_TTL:
            scores = leaderboard_cache['data']

    if scores is not None:
        return render_template('leaderboard.html', scores=scores)

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
            leaderboard_cache['timestamp'] = time.time()

    except Exception as e:
        scores = []
        current_app.logger.error(f"Error fetching leaderboard: {e}")

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
