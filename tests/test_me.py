def test_logged_off_client_cannot_get_itself(client):
    resp = client.get('/api/me')
    assert resp.status_code == 401


def test_logged_in_client_can_get_itself(client_with_tok):
    resp = client_with_tok.get('/api/me')
    assert resp.status_code == 200


def test_client_corretly_gets_itself(client_with_tok_getter):
    client_with_tok = client_with_tok_getter('user')
    resp = client_with_tok.get('/api/me')
    assert resp.json['data']['username'] == 'user'


def test_client_gets_correct_user_fields_for_itself(client_with_tok):
    resp = client_with_tok.get('/api/me')
    assert 'data' in resp.json
    assert {
        'user_id',
        'username',
        'signature',
        'roles',
        'avatar',
        'status',
        'created_at',
        'updated_at',
    } == set(resp.json['data'].keys())
