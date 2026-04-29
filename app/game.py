from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for, flash
from supabase import create_client, Client, ClientOptions
import os

game_bp = Blueprint('game', __name__)

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

    user_client = None
    try:
        # Create a new client instance authenticated as the user
        # This ensures RLS policies are respected correctly
        # Pass headers via ClientOptions
        user_client: Client = create_client(
            url,
            key,
            options=ClientOptions(headers={"Authorization": f"Bearer {token}"})
        )

        response = user_client.table("scores").insert({
            "user_id": user_id,
            "score": score
        }).execute()

        return jsonify({"message": "Score submitted successfully", "data": response.data}), 200

    except Exception as e:
        print(f"Error submitting score: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Explicitly close the underlying HTTP connections to prevent connection pool
        # leaks and memory bloat over time since a new client is created per request
        if user_client:
            if hasattr(user_client, 'auth') and hasattr(user_client.auth, '_http_client'):
                user_client.auth._http_client.close()
            if hasattr(user_client, 'postgrest') and hasattr(user_client.postgrest, 'session'):
                user_client.postgrest.session.close()
            if hasattr(user_client, 'storage') and hasattr(user_client.storage, 'session'):
                user_client.storage.session.close()
