from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase
import time
import threading

main_bp = Blueprint('main', __name__)

# Cache for leaderboard to prevent database overload
# TTL cache prevents stampedes using a lock
leaderboard_cache = {
    'data': [],
    'timestamp': 0
}
leaderboard_cache_lock = threading.Lock()
CACHE_TTL = 30  # seconds

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    # Fast path: check cache outside lock
    current_time = time.time()
    if current_time - leaderboard_cache['timestamp'] < CACHE_TTL:
        scores = leaderboard_cache['data']
    else:
        # Slow path: acquire lock to update cache (prevents stampede)
        with leaderboard_cache_lock:
            # Double check inside lock in case another thread just updated it
            current_time = time.time()
            if current_time - leaderboard_cache['timestamp'] < CACHE_TTL:
                scores = leaderboard_cache['data']
            else:
                try:
                    # Bolt: Optimized with in-memory TTL cache to reduce DB load
                    # Impact: Significantly reduces backend latency and DB query costs for a read-heavy endpoint
                    response = supabase.table('scores') \
                        .select('score, created_at, profiles(username, avatar_url)') \
                        .order('score', desc=True) \
                        .limit(10) \
                        .execute()

                    scores = response.data
                    leaderboard_cache['data'] = scores
                    leaderboard_cache['timestamp'] = current_time
                except Exception as e:
                    # Fallback to old cache if available, otherwise empty list
                    scores = leaderboard_cache['data'] if leaderboard_cache['data'] else []
                    print(f"Error fetching leaderboard: {e}")

    # render_template is expensive, do it outside the lock
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
