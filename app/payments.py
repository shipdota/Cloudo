from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import stripe
import os
from .db import supabase

payments_bp = Blueprint('payments', __name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

@payments_bp.route('/pricing')
def pricing():
    # If user is logged in, check if they are already pro
    is_pro = False
    if 'user' in session:
        from app.chat import get_user_supabase_client
        user_client = get_user_supabase_client()
        if user_client:
            try:
                user_id = session['user']['id']
                profile_res = user_client.table('profiles').select('is_pro').eq('id', user_id).single().execute()
                is_pro = profile_res.data.get('is_pro', False)
            except Exception as e:
                print(f"Error fetching profile: {e}")

    return render_template('pricing.html', is_pro=is_pro)

@payments_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user']['id']
    user_email = session['user']['email']
    price_id = os.environ.get("STRIPE_PRICE_ID")

    if not price_id:
        flash("Stripe Price ID is not configured.", "danger")
        return redirect(url_for('payments.pricing'))

    try:
        # Check if user already has a Stripe Customer ID
        from app.chat import get_user_supabase_client
        user_client = get_user_supabase_client()
        if not user_client:
             flash("Failed to authenticate with database.", "danger")
             return redirect(url_for('payments.pricing'))

        profile_res = user_client.table('profiles').select('stripe_customer_id').eq('id', user_id).single().execute()
        stripe_customer_id = profile_res.data.get('stripe_customer_id')

        if not stripe_customer_id:
            customer = stripe.Customer.create(
                email=user_email,
                metadata={'supabase_user_id': user_id}
            )
            stripe_customer_id = customer.id
            from app.chat import get_user_supabase_client
            user_client = get_user_supabase_client()
            if user_client:
                user_client.table('profiles').update({'stripe_customer_id': stripe_customer_id}).eq('id', user_id).execute()

        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=request.url_root + 'chat?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.url_root + 'pricing',
            client_reference_id=user_id,
        )

        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        flash("Could not start checkout process.", "danger")
        return redirect(url_for('payments.pricing'))

@payments_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # To update profiles via webhook, we need service role privileges to bypass RLS
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not service_role_key:
        print("Warning: SUPABASE_SERVICE_ROLE_KEY not set. Webhooks may fail to update RLS-protected tables.")
        service_client = supabase
    else:
        from supabase import create_client
        service_client = create_client(os.environ.get("SUPABASE_URL"), service_role_key)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']

        user_id = session_obj.get('client_reference_id')
        if not user_id:
             # Try to get it from customer metadata
             customer_id = session_obj.get('customer')
             if customer_id:
                 try:
                     customer = stripe.Customer.retrieve(customer_id)
                     user_id = customer.metadata.get('supabase_user_id')
                 except Exception as e:
                     print(f"Error retrieving customer: {e}")

        if user_id:
            try:
                # Update user profile to be pro using service client
                service_client.table('profiles').update({'is_pro': True}).eq('id', user_id).execute()
                print(f"Successfully upgraded user {user_id} to pro.")
            except Exception as e:
                print(f"Error updating user to pro in DB: {e}")

    # Handle subscription cancellation
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')

        if customer_id:
            try:
                # We need to find the user by stripe_customer_id
                profile_res = service_client.table('profiles').select('id').eq('stripe_customer_id', customer_id).single().execute()
                user_id = profile_res.data.get('id')
                if user_id:
                    service_client.table('profiles').update({'is_pro': False}).eq('id', user_id).execute()
                    print(f"Successfully revoked pro status for user {user_id}.")
            except Exception as e:
                print(f"Error revoking pro status in DB: {e}")

    return jsonify(success=True)
