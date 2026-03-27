import time
from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase

main_bp = Blueprint('main', __name__)

# Bolt: In-memory cache for leaderboard to reduce latency
_leaderboard_cache = {
    "data": [],
    "expiry": 0
}
CACHE_TTL = 60 # seconds

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    start_time = time.time()
    now = time.time()

    if _leaderboard_cache["expiry"] > now:
        scores = _leaderboard_cache["data"]
        latency = (time.time() - start_time) * 1000
        print(f"⚡ Bolt: Leaderboard cache hit. Latency: {latency:.2f}ms", flush=True)
    else:
        try:
            # Fetch top 10 scores with user details
            response = supabase.table('scores') \
                .select('score, created_at, profiles(username, avatar_url)') \
                .order('score', desc=True) \
                .limit(10) \
                .execute()

            scores = response.data
            _leaderboard_cache["data"] = scores
            _leaderboard_cache["expiry"] = now + CACHE_TTL

            latency = (time.time() - start_time) * 1000
            print(f"⚡ Bolt: Leaderboard cache miss. Latency: {latency:.2f}ms", flush=True)
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
