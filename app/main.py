from flask import Blueprint, render_template, session, redirect, url_for
from cachetools import cached, TTLCache
from .db import supabase

main_bp = Blueprint('main', __name__)

# Cache leaderboard data for 60 seconds
leaderboard_cache = TTLCache(maxsize=1, ttl=60)

@cached(leaderboard_cache)
def get_leaderboard_data():
    try:
        # Fetch top 10 scores with user details
        response = supabase.table('scores') \
            .select('score, created_at, profiles(username, avatar_url)') \
            .order('score', desc=True) \
            .limit(10) \
            .execute()

        return response.data
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return []

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
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
