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

@patch('app.main.supabase')
def test_leaderboard_caching(mock_supabase, client):
    # Mock data
    mock_data = [
        {'score': 100, 'created_at': '2023-01-01', 'profiles': {'username': 'Player1', 'avatar_url': ''}}
    ]

    # Mock the execute() result
    mock_execute = MagicMock()
    mock_execute.data = mock_data

    # Setup chain: table -> select -> order -> limit -> execute
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_order = MagicMock()
    mock_limit = MagicMock()

    mock_supabase.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.order.return_value = mock_order
    mock_order.limit.return_value = mock_limit
    mock_limit.execute.return_value = mock_execute

    # First call - should hit the mock
    response1 = client.get('/leaderboard')
    assert response1.status_code == 200
    assert b"Player1" in response1.data

    # Verify mock was called
    assert mock_supabase.table.call_count == 1

    # Second call - should use cache and NOT hit the mock again
    response2 = client.get('/leaderboard')
    assert response2.status_code == 200
    assert b"Player1" in response2.data

    # Verify mock was NOT called again (call count should still be 1)
    assert mock_supabase.table.call_count == 1

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
