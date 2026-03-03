import pytest
from unittest.mock import patch, MagicMock
from flask import session

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to" in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_game_page_unauthorized(client):
    # Should redirect to login
    response = client.get('/game', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"You must be logged in to play." in response.data

def test_game_page_authorized(client):
    with client.session_transaction() as sess:
        sess['user'] = {'id': '123', 'email': 'test@example.com', 'username': 'tester', 'access_token': 'fake', 'refresh_token': 'fake'}

    response = client.get('/game')
    assert response.status_code == 200
    assert b"Ready to Test Your Reflexes?" in response.data

@patch('app.auth.supabase')
def test_login_post_success(mock_supabase, client):
    # Mock the sign_in_with_password response
    mock_response = MagicMock()
    mock_response.user.id = '123'
    mock_response.user.email = 'test@example.com'
    mock_response.session.access_token = 'fake-token'
    mock_response.session.refresh_token = 'fake-refresh'

    # Setup the return value for sign_in_with_password
    mock_supabase.auth.sign_in_with_password.return_value = mock_response

    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Logged in successfully!" in response.data

    with client.session_transaction() as sess:
        assert sess['user']['email'] == 'test@example.com'

@patch('app.main.supabase')
def test_leaderboard(mock_supabase, client):
    # Mock data
    mock_data = [
        {'score': 100, 'created_at': '2023-01-01', 'profiles': {'username': 'Player1', 'avatar_url': ''}},
        {'score': 50, 'created_at': '2023-01-02', 'profiles': {'username': 'Player2', 'avatar_url': ''}}
    ]

    # Mock the execute() result
    mock_execute = MagicMock()
    mock_execute.data = mock_data

    # Setup chain: table -> select -> order -> limit -> execute
    # We must configure the chain carefully because each call returns a mock that must respond to the next call

    # Create the chain of mocks
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_order = MagicMock()
    mock_limit = MagicMock()

    mock_supabase.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.order.return_value = mock_order
    mock_order.limit.return_value = mock_limit
    mock_limit.execute.return_value = mock_execute

    response = client.get('/leaderboard')
    assert response.status_code == 200
    assert b"Player1" in response.data
    assert b"100" in response.data

@patch('app.game.create_client')
def test_submit_score(mock_create_client, client):
    # Setup mock user session
    with client.session_transaction() as sess:
        sess['user'] = {'id': '123', 'email': 'test@example.com', 'username': 'tester', 'access_token': 'fake', 'refresh_token': 'fake'}

    # Mock client and insert
    mock_client_instance = MagicMock()
    mock_create_client.return_value = mock_client_instance

    mock_insert_response = MagicMock()
    mock_insert_response.data = [{'id': 1, 'score': 50}]

    mock_client_instance.table.return_value.insert.return_value.execute.return_value = mock_insert_response

    response = client.post('/api/submit-score', json={'score': 50})

    assert response.status_code == 200
    assert b"Score submitted successfully" in response.data


@patch('app.main.supabase')
def test_profile_shows_performance_snapshot(mock_supabase, client):
    with client.session_transaction() as sess:
        sess['user'] = {'id': '123', 'email': 'test@example.com', 'username': 'tester', 'access_token': 'fake', 'refresh_token': 'fake'}

    # profile query
    profile_execute = MagicMock()
    profile_execute.data = {
        'id': '123',
        'username': 'tester',
        'avatar_url': '',
        'created_at': '2023-01-01T00:00:00'
    }

    # top scores query
    top_scores_execute = MagicMock()
    top_scores_execute.data = [
        {'score': 60, 'created_at': '2023-01-10'},
        {'score': 30, 'created_at': '2023-01-09'},
    ]

    # all scores query
    all_scores_execute = MagicMock()
    all_scores_execute.data = [{'score': 60}, {'score': 30}, {'score': 10}]

    # Configure chain for profile lookup
    mock_profile_table = MagicMock()
    mock_profile_select = MagicMock()
    mock_profile_eq = MagicMock()
    mock_profile_single = MagicMock()

    mock_profile_table.select.return_value = mock_profile_select
    mock_profile_select.eq.return_value = mock_profile_eq
    mock_profile_eq.single.return_value = mock_profile_single
    mock_profile_single.execute.return_value = profile_execute

    # Configure chain for top scores lookup
    mock_top_scores_table = MagicMock()
    mock_top_scores_select = MagicMock()
    mock_top_scores_eq = MagicMock()
    mock_top_scores_order = MagicMock()
    mock_top_scores_limit = MagicMock()

    mock_top_scores_table.select.return_value = mock_top_scores_select
    mock_top_scores_select.eq.return_value = mock_top_scores_eq
    mock_top_scores_eq.order.return_value = mock_top_scores_order
    mock_top_scores_order.limit.return_value = mock_top_scores_limit
    mock_top_scores_limit.execute.return_value = top_scores_execute

    # Configure chain for all scores lookup
    mock_all_scores_table = MagicMock()
    mock_all_scores_select = MagicMock()
    mock_all_scores_eq = MagicMock()

    mock_all_scores_table.select.return_value = mock_all_scores_select
    mock_all_scores_select.eq.return_value = mock_all_scores_eq
    mock_all_scores_eq.execute.return_value = all_scores_execute

    mock_supabase.table.side_effect = [
        mock_profile_table,
        mock_top_scores_table,
        mock_all_scores_table,
    ]

    response = client.get('/profile')

    assert response.status_code == 200
    assert b"Performance Snapshot" in response.data
    assert b"Skilled Hunter" in response.data
    assert b"3" in response.data  # games played
    assert b"33.3" in response.data  # average score
