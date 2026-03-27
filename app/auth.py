from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .db import supabase
from supabase_auth.errors import AuthApiError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')

        try:
            # Sign up with Supabase
            res = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"username": username}
                }
            })

            # If auto-confirm is on (default for some setups), we might be logged in.
            # But usually it requires email confirmation.
            # Check if session exists in response
            if res.session:
                session['user'] = {
                    'id': res.user.id,
                    'email': res.user.email,
                    'access_token': res.session.access_token,
                    'refresh_token': res.session.refresh_token,
                    'username': username
                }
                flash('Registration successful! Welcome.', 'success')
                return redirect(url_for('main.index')) # We'll create main.index later
            else:
                flash('Registration successful! Please check your email to confirm.', 'info')
                return redirect(url_for('auth.login'))

        except AuthApiError as e:
            flash(f'Error: {e.message}', 'danger')
        except Exception as e:
            flash(f'An unexpected error occurred: {str(e)}', 'danger')

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            session['user'] = {
                'id': res.user.id,
                'email': res.user.email,
                'access_token': res.session.access_token,
                'refresh_token': res.session.refresh_token,
                # We can fetch profile later if needed, or store it now if we query it
            }

            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index')) # Placeholder

        except AuthApiError as e:
            flash(f'Login failed: {e.message}', 'danger')
        except Exception as e:
            flash(f'An unexpected error occurred: {str(e)}', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
