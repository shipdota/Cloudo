from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash
from supabase import create_client, Client, ClientOptions
import os
import functools

game_bp = Blueprint('game', __name__)

@functools.lru_cache(maxsize=128)
def get_user_client(url: str, key: str, token: str) -> Client:
    """Cache the Supabase client to avoid expensive instantiation per request."""
    return create_client(
        url,
        key,
        options=ClientOptions(headers={"Authorization": f"Bearer {token}"})
    )

@game_bp.route('/game')
def game():
    if 'user' not in session:
        flash("You must be logged in to play.", "danger")
        return redirect(url_for('auth.login'))
    return render_template('game.html')

@game_bp.route('/api/submit-score', methods=['POST'])
def submit_score():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    score = data.get('score')

    if score is None:
        return jsonify({"error": "Invalid data"}), 400

    user_id = session['user']['id']
    token = session['user']['access_token']

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    try:
        # Get cached client authenticated as the user
        # This ensures RLS policies are respected correctly without the
        # overhead of creating a new httpx.Client on every request
        user_client: Client = get_user_client(url, key, token)

        response = user_client.table("scores").insert({
            "user_id": user_id,
            "score": score
        }).execute()

        return jsonify({"message": "Score submitted successfully", "data": response.data}), 200

    except Exception as e:
        print(f"Error submitting score: {e}")
        return jsonify({"error": str(e)}), 500
