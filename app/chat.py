from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from supabase import create_client, Client, ClientOptions
from openai import OpenAI
import os

chat_bp = Blueprint('chat', __name__)

# Initialize OpenAI client
# It will automatically pick up OPENAI_API_KEY from environment
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    openai_client = None


def get_user_supabase_client():
    if 'user' not in session:
        return None
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    token = session['user']['access_token']
    return create_client(
        url,
        key,
        options=ClientOptions(headers={"Authorization": f"Bearer {token}"})
    )

@chat_bp.route('/chat')
def chat_ui():
    if 'user' not in session:
        flash("You must be logged in to use the chat.", "danger")
        return redirect(url_for('auth.login'))

    # Check if user is pro
    user_id = session['user']['id']
    user_client = get_user_supabase_client()

    if not user_client:
        flash("Failed to authenticate with database.", "danger")
        return redirect(url_for('auth.login'))

    try:
        profile_res = user_client.table('profiles').select('is_pro').eq('id', user_id).single().execute()
        is_pro = profile_res.data.get('is_pro', False)

        if not is_pro:
            return redirect(url_for('payments.pricing'))

    except Exception as e:
        print(f"Error checking profile status: {e}")
        flash("An error occurred while checking your subscription.", "danger")
        return redirect(url_for('main.index'))

    return render_template('chat.html')

@chat_bp.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_client = get_user_supabase_client()
    if not user_client:
        return jsonify({"error": "Failed to authenticate"}), 401

    try:
        response = user_client.table('chat_messages').select('*').order('created_at', desc=False).execute()
        return jsonify({"messages": response.data})
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/api/chat', methods=['POST'])
def send_message():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_client = get_user_supabase_client()
    if not user_client:
        return jsonify({"error": "Failed to authenticate"}), 401

    # Check if user is pro
    user_id = session['user']['id']

    try:
        profile_res = user_client.table('profiles').select('is_pro').eq('id', user_id).single().execute()
        is_pro = profile_res.data.get('is_pro', False)
        if not is_pro:
            return jsonify({"error": "Subscription required", "redirect": url_for('payments.pricing')}), 403
    except Exception as e:
        print(f"Error checking pro status for chat API: {e}")
        return jsonify({"error": "Database error"}), 500

    data = request.get_json()
    message_content = data.get('message')

    if not message_content:
        return jsonify({"error": "Message is required"}), 400

    if not openai_client:
        return jsonify({"error": "OpenAI not configured"}), 500

    try:
        # Save user message to Supabase
        user_msg_res = user_client.table('chat_messages').insert({
            'user_id': user_id,
            'role': 'user',
            'content': message_content
        }).execute()

        # Fetch previous context (last 10 messages to save tokens)
        history_res = user_client.table('chat_messages').select('role, content').order('created_at', desc=True).limit(10).execute()

        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

        # History is ordered desc, so we need to reverse it for OpenAI
        if history_res and history_res.data:
             for msg in reversed(history_res.data):
                  messages.append({"role": msg['role'], "content": msg['content']})

        messages.append({"role": "user", "content": message_content})

        # Call OpenAI
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        ai_response_content = completion.choices[0].message.content

        # Save AI response to Supabase
        ai_msg_res = user_client.table('chat_messages').insert({
            'user_id': user_id,
            'role': 'assistant',
            'content': ai_response_content
        }).execute()

        return jsonify({
            "message": ai_response_content,
            "id": ai_msg_res.data[0]['id']
        })

    except Exception as e:
        print(f"Error handling chat message: {e}")
        return jsonify({"error": str(e)}), 500
