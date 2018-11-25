def test_unregistered_user_cannot_login_with_username(client):
    resp = client.post('/api/auth/login',
        data={'username': 'unregistered', 'password': 'testpass'})
    assert resp.status_code == 400


def test_unregistered_user_cannot_login_with_email(client):
    resp = client.post('/api/auth/login',
        data={'username': 'wrong@wrongmail.com', 'password': 'testpass'})
    assert resp.status_code == 400


def test_registered_user_can_login_with_username(client):
    resp = client.post('/api/auth/login',
        data={
            'username': 'user',
            'password': 'testpass'
        }
    )
    assert resp.status_code == 200
    assert 'access_token' in resp.json
    assert 'refresh_token' in resp.json


def test_registered_user_can_login_with_email(client):
    resp = client.post('/api/auth/login',
        data={
            'email': 'user@users.com',
            'password': 'testpass'
        }
    )
    assert resp.status_code == 200
    assert 'access_token' in resp.json
    assert 'refresh_token' in resp.json


def test_logged_in_user_can_logoff(client_with_tok):
    resp = client_with_tok.post('/api/auth/logout')
    assert resp.status_code == 204


def test_logged_in_user_cannot_use_revoked_token_after_logoff(client_with_tok):
    resp_1 = client_with_tok.get('/api/auth/ok')
    resp_2 = client_with_tok.post('/api/auth/logout')
    resp_3 = client_with_tok.get('/api/auth/ok')
    assert resp_3.status_code == 401


def test_logged_in_user_can_refresh_token(client_with_refresh_tok):
    resp = client_with_refresh_tok.post('/api/auth/token_refresh')
    assert resp.status_code == 200
    assert 'access_token' in resp.json


def test_logged_in_user_can_use_new_token(client, refresh_token):
    resp_1 = client.post('/api/auth/token_refresh',
        headers={
            'Authorization': 'Bearer {}'.format(refresh_token),
        }
    )
    resp_2 = client.get('/api/auth/ok',
        headers={
            'Authorization': 'Bearer {}'.format(resp_1.json['access_token'])
        }
    )
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200
