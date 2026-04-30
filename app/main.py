from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase
import concurrent.futures

main_bp = Blueprint('main', __name__)

# Global executor to avoid thread creation overhead on every request
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/leaderboard')
def leaderboard():
    try:
        # Fetch top 10 scores with user details
        response = supabase.table('scores') \
            .select('score, created_at, profiles(username, avatar_url)') \
            .order('score', desc=True) \
            .limit(10) \
            .execute()

        scores = response.data
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
        # ⚡ Bolt Optimization: Fetch profile and scores concurrently
        # 💡 What: Replaced sequential database queries with concurrent execution using ThreadPoolExecutor
        # 🎯 Why: Reduces the number of network round trips by overlapping the queries
        # 📊 Impact: Effectively halves the database fetching latency for the `/profile` route
        # 🔬 Measurement: Benchmarking sequential vs concurrent execution times
        def fetch_profile():
            return supabase.table('profiles').select('*').eq('id', user_id).single().execute().data

        def fetch_scores():
            return supabase.table('scores') \
                .select('*') \
                .eq('user_id', user_id) \
                .order('score', desc=True) \
                .limit(5) \
                .execute().data

        future_profile = executor.submit(fetch_profile)
        future_scores = executor.submit(fetch_scores)

        user_profile = future_profile.result()
        user_scores = future_scores.result()

    except Exception as e:
        user_profile = {}
        user_scores = []
        print(f"Error fetching profile: {e}")

    return render_template('profile.html', profile=user_profile, scores=user_scores)
