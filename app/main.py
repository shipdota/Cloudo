from flask import Blueprint, render_template, session, redirect, url_for
from .db import supabase

main_bp = Blueprint('main', __name__)


def _calculate_player_tier(best_score, games_played):
    if best_score >= 75:
        return "Elite Operative"
    if best_score >= 40:
        return "Skilled Hunter"
    if games_played >= 5:
        return "Rising Agent"
    return "Rookie"

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

        all_scores_res = supabase.table('scores') \
            .select('score') \
            .eq('user_id', user_id) \
            .execute()
        all_scores = [row.get('score', 0) for row in all_scores_res.data or []]

        games_played = len(all_scores)
        best_score = max(all_scores) if all_scores else 0
        average_score = round(sum(all_scores) / games_played, 1) if games_played else 0
        player_tier = _calculate_player_tier(best_score, games_played)

    except Exception as e:
        user_profile = {}
        user_scores = []
        games_played = 0
        best_score = 0
        average_score = 0
        player_tier = "Rookie"
        print(f"Error fetching profile: {e}")

    return render_template(
        'profile.html',
        profile=user_profile,
        scores=user_scores,
        games_played=games_played,
        best_score=best_score,
        average_score=average_score,
        player_tier=player_tier,
    )
