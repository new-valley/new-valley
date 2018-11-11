def test_client_can_get_avatars(client):
    resp = client.get('/api/avatars')
    assert resp.status_code == 200


def test_client_gets_correct_avatars_fields(client):
    resp = client.get('/api/avatars')
    assert 'offset' in resp.json
    assert resp.json['offset'] is None
    assert 'total' in resp.json
    assert 'data' in resp.json
    assert resp.json['total'] == len(resp.json['data'])
    assert {
        'avatar_id',
        'category',
        'uri',
        'created_at',
        'updated_at',
    } == set(resp.json['data'][0].keys())


def test_client_filters_avatars_fields(client):
    resp = client.get('/api/avatars?fields=category,created_at')
    avatars = resp.json['data']
    assert {
        'category',
        'created_at',
    } == set(avatars[0].keys())


def test_client_offsets_avatars(client):
    resp_1 = client.get('/api/avatars')
    resp_2 = client.get('/api/avatars?offset=2')
    assert len(resp_1.json['data']) \
        == len(resp_2.json['data']) + min(2, len(resp_1.json['data']))
    

def test_client_limits_avatars(client):
    resp_1 = client.get('/api/avatars?max_n_results=1')
    resp_2 = client.get('/api/avatars?max_n_results=2')
    assert len(resp_1.json['data']) <= 1
    assert len(resp_2.json['data']) <= 2


def test_logged_off_client_cannot_create_avatar(client):
    resp = client.post('/api/avatars',
        data={
            'uri': 'http://newavatars.com/img.png',
            'category': 'dummy',
        }
    )
    assert resp.status_code == 401


def test_logged_in_user_cannot_create_avatar(client_with_tok):
    resp = client_with_tok.post('/api/avatars',
        data={
            'uri': 'http://newavatars.com/img.png',
            'category': 'dummy',
        }
    )
    assert resp.status_code == 401


def test_logged_in_mod_cannot_create_avatar(mod_with_tok):
    resp = mod_with_tok.post('/api/avatars',
        data={
            'uri': 'http://newavatars.com/img.png',
            'category': 'dummy',
        }
    )
    assert resp.status_code == 401


def test_logged_in_admin_can_create_avatar(admin_with_tok):
    resp = admin_with_tok.post('/api/avatars',
        data={
            'uri': 'http://newavatars.com/img.png',
            'category': 'dummy',
        }
    )
    assert resp.status_code == 200


def test_logged_in_admin_gets_correct_data_on_user_creation(admin_with_tok):
    resp = admin_with_tok.post('/api/avatars',
        data={
            'uri': 'http://newavatars.com/img.png',
            'category': 'dummy',
        }
    )
    assert 'data' in resp.json
    assert resp.json['data']['uri'] == 'http://newavatars.com/img.png'
    assert resp.json['data']['category'] == 'dummy'


def test_client_can_get_avatar(client, avatar_id):
    resp = client.get('/api/avatars/{}'.format(avatar_id))
    assert resp.status_code == 200
    assert 'data' in resp.json


def test_client_gets_correct_avatar_fields(client, avatar_id):
    resp = client.get('/api/avatars/{}'.format(avatar_id))
    assert 'data' in resp.json
    assert {
        'avatar_id',
        'category',
        'uri',
        'created_at',
        'updated_at',
    } == set(resp.json['data'].keys())


def test_logged_off_client_cannot_edit_avatar(client, avatar_id):
    resp = client.put('/api/avatars/{}'.format(avatar_id),
        data={
            'uri': 'http://newavatars.com/newimg.png',
        }
    )
    assert resp.status_code == 401


def test_logged_in_user_cannot_edit_avatar(client_with_tok, avatar_id):
    resp = client_with_tok.put('/api/avatars/{}'.format(avatar_id),
        data={
            'uri': 'http://newavatars.com/newimg.png',
        }
    )
    assert resp.status_code == 401


def test_logged_in_mod_cannot_edit_avatar(mod_with_tok, avatar_id):
    resp = mod_with_tok.put('/api/avatars/{}'.format(avatar_id),
        data={
            'uri': 'http://newavatars.com/newimg.png',
        }
    )
    assert resp.status_code == 401


def test_logged_in_admin_can_edit_avatar(admin_with_tok, avatar_id):
    resp = admin_with_tok.put('/api/avatars/{}'.format(avatar_id),
        data={
            'uri': 'http://newavatars.com/img.png',
            'category': 'dummy',
        }
    )
    assert resp.status_code == 200


def test_logged_in_admin_gets_correct_put_fields(admin_with_tok, avatar_id):
    resp = admin_with_tok.put('/api/avatars/{}'.format(avatar_id),
        data={
            'category': 'newcategory',
        }
    )
    assert 'data' in resp.json
    assert {
        'avatar_id',
        'category',
        'uri',
        'created_at',
        'updated_at',
    } == set(resp.json['data'].keys())


def test_logged_in_admin_corretly_edits_avatar(admin_with_tok, avatar_id):
    resp_1 = admin_with_tok.get('/api/avatars/{}'.format(avatar_id))
    resp_2 = admin_with_tok.put('/api/avatars/{}'.format(avatar_id),
        data={
            'category': resp_1.json['data']['category'] + '_altered',
            'uri': resp_1.json['data']['uri'] + '.png',
        }
    )
    resp_3 = admin_with_tok.get('/api/avatars/{}'.format(avatar_id))
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200
    assert resp_3.status_code == 200
    assert resp_3.json['data']['category'] \
        == resp_1.json['data']['category'] + '_altered'
    assert resp_3.json['data']['uri'] \
        == resp_1.json['data']['uri'] + '.png'
