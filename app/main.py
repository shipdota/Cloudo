import time
import threading
from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase

main_bp = Blueprint('main', __name__)

# Cache for leaderboard to reduce database load
_leaderboard_cache = None
_leaderboard_cache_time = 0
_leaderboard_cache_lock = threading.Lock()
CACHE_TTL = 60 # seconds

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    global _leaderboard_cache, _leaderboard_cache_time

    # ⚡ Bolt Optimization:
    # 💡 What: Implement thread-safe in-memory TTL cache using double-checked locking
    # 🎯 Why: Prevents repeated identical database queries for a global read-heavy endpoint
    # 📊 Impact: Significantly reduces database load during high traffic

    current_time = time.time()

    # Fast path: check if cache is valid without acquiring lock
    if _leaderboard_cache is None or (current_time - _leaderboard_cache_time) > CACHE_TTL:
        with _leaderboard_cache_lock:
            # Double-checked locking to prevent cache stampedes
            if _leaderboard_cache is None or (time.time() - _leaderboard_cache_time) > CACHE_TTL:
                try:
                    # Fetch top 10 scores with user details
                    response = supabase.table('scores') \
                        .select('score, created_at, profiles(username, avatar_url)') \
                        .order('score', desc=True) \
                        .limit(10) \
                        .execute()

                    _leaderboard_cache = response.data
                    _leaderboard_cache_time = time.time()
                except Exception as e:
                    print(f"Error fetching leaderboard: {e}")
                    if _leaderboard_cache is None:
                        _leaderboard_cache = []

    # Get cached value
    scores = _leaderboard_cache

    # Render template entirely outside the lock
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
