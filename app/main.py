from flask import Blueprint, render_template, session, redirect, url_for
import time
from .db import supabase

main_bp = Blueprint('main', __name__)

# Simple in-memory cache for the leaderboard
# TTL of 60 seconds to reduce database overhead
leaderboard_cache = {
    'data': None,
    'timestamp': 0
}
CACHE_TTL = 60

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    current_time = time.time()

    # Check cache first
    if leaderboard_cache['data'] is not None and (current_time - leaderboard_cache['timestamp']) < CACHE_TTL:
        print("Leaderboard cache hit", flush=True)
        scores = leaderboard_cache['data']
    else:
        print("Leaderboard cache miss", flush=True)
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

        except Exception as e:
            scores = []
            print(f"Error fetching leaderboard: {e}", flush=True)

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
