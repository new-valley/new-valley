def test_client_can_get_users(client):
    resp = client.get('/api/users')
    assert resp.status_code == 200


def test_client_gets_correct_users_fields(client):
    resp = client.get('/api/users')
    assert 'offset' in resp.json
    assert resp.json['offset'] is None
    assert 'total' in resp.json
    assert 'data' in resp.json
    assert len(resp.json['data']) > 0
    assert resp.json['total'] == len(resp.json['data'])
    assert {
        'user_id',
        'username',
        'signature',
        'roles',
        'avatar',
        'status',
        'n_posts',
        'n_topics',
        'created_at',
        'updated_at',
    } == set(resp.json['data'][0].keys())


def test_client_filters_users_fields(client):
    resp = client.get('/api/users?fields=username,signature')
    users = resp.json['data']
    assert {
        'username',
        'signature',
    } == set(users[0].keys())


def test_client_offsets_users(client):
    resp_1 = client.get('/api/users')
    resp_2 = client.get('/api/users?offset=2')
    assert len(resp_1.json['data']) \
        == len(resp_2.json['data']) + min(2, len(resp_1.json['data']))


def test_client_limits_users(client):
    resp_1 = client.get('/api/users?max_n_results=1')
    resp_2 = client.get('/api/users?max_n_results=2')
    assert len(resp_1.json['data']) <= 1
    assert len(resp_2.json['data']) <= 2


def test_client_can_create_user(client):
    resp = client.post('/api/users',
        data={
            'username': 'test',
            'password': 'testpass',
            'email': 'foo@bar.com',
        }
    )
    assert resp.status_code == 200


def test_client_gets_correct_data_on_user_creation(client):
    resp = client.post('/api/users',
        data={
            'username': 'test',
            'password': 'testpass',
            'email': 'foo@bar.com',
        }
    )
    assert 'data' in resp.json
    assert resp.json['data']['username'] == 'test'
    assert 'email' not in resp.json['data']
    assert 'password' not in resp.json['data']


def test_client_cannot_overwrite_user(client):
    resp_1 = client.post('/api/users',
        data={
            'username': 'test',
            'password': 'testpass',
            'email': 'foo@bar.com',
        }
    )
    resp_2 = client.post('/api/users',
        data={
            'username': 'test',
            'password': 'testpass2',
            'email': 'foo@bar.com',
        }
    )
    resp_3 = client.post('/api/users',
        data={
            'username': 'test2',
            'password': 'testpass3',
            'email': 'foo@bar.com',
        }
    )
    resp_4 = client.post('/api/users',
        data={
            'username': 'test',
            'password': 'testpass4',
            'email': 'foo2@bar.com',
        }
    )
    assert resp_1.status_code == 200
    assert resp_2.status_code == 400
    assert resp_3.status_code == 400
    assert resp_4.status_code == 400


def test_client_cannot_create_user_with_missing_fields(client):
    resp_1 = client.post('/api/users',
        data={
            'password': 'testpass',
            'email': 'foo@bar.com',
        }
    )
    resp_2 = client.post('/api/users',
        data={
            'username': 'test',
            'email': 'foo@bar.com',
        }
    )
    resp_3 = client.post('/api/users',
        data={
            'username': 'test',
            'password': 'testpass',
        }
    )
    assert resp_1.status_code == 400
    assert resp_2.status_code == 400
    assert resp_3.status_code == 400


def test_client_cannot_create_user_referencing_nonexistent_avatar(client):
    resp = client.post('/api/users',
        data={
            'username': 'test',
            'password': 'testpass',
            'email': 'foo@bar.com',
            'avatar_id': 999999,
        }
    )
    assert resp.status_code == 400


def test_client_can_get_user(client, user_id):
    resp = client.get('/api/users/{}'.format(user_id))
    assert resp.status_code == 200


def test_client_gets_correct_user_fields(client, user_id):
    resp = client.get('/api/users/{}'.format(user_id))
    assert 'data' in resp.json
    assert {
        'user_id',
        'username',
        'signature',
        'roles',
        'avatar',
        'status',
        'n_posts',
        'n_topics',
        'created_at',
        'updated_at',
    } == set(resp.json['data'].keys())


def test_logged_off_client_cannot_delete_user(client, user_id):
    resp = client.delete('/api/users/{}'.format(user_id))
    assert resp.status_code == 401


def test_logged_in_client_can_delete_its_user(
        client_with_tok_getter, user_id_getter):
    client_with_tok = client_with_tok_getter('user')
    user_id = user_id_getter('user')
    resp = client_with_tok.delete('/api/users/{}'.format(user_id))
    assert resp.status_code == 204


def test_logged_in_user_cannot_delete_other_user(
        client_with_tok_getter, user_id_getter):
    client_with_tok = client_with_tok_getter('user')
    other_user_id = user_id_getter('user_b')
    resp = client_with_tok.delete('/api/users/{}'.format(other_user_id))
    assert resp.status_code == 401


def test_logged_in_mod_cannot_delete_other_user(mod_with_tok, user_id_getter):
    other_user_id = user_id_getter('user_b')
    resp = mod_with_tok.delete('/api/users/{}'.format(other_user_id))
    assert resp.status_code == 401


def test_logged_in_admin_can_delete_other_user(admin_with_tok, user_id_getter):
    other_user_id = user_id_getter('user_b')
    resp = admin_with_tok.delete('/api/users/{}'.format(other_user_id))
    assert resp.status_code == 204


def test_logged_in_admin_corretly_deletes_user(admin_with_tok, user_id):
    resp_1 = admin_with_tok.get('/api/users/{}'.format(user_id))
    resp_2 = admin_with_tok.delete('/api/users/{}'.format(user_id))
    resp_3 = admin_with_tok.get('/api/users/{}'.format(user_id))
    assert resp_1.status_code == 200
    assert resp_2.status_code == 204
    assert resp_3.status_code == 404


def test_logged_off_client_cannot_edit_user(client, user_id):
    resp = client.put('/api/users/{}'.format(user_id),
        data={
            'username': 'newusername',
        }
    )
    assert resp.status_code == 401


def test_logged_in_client_can_edit_its_user(
        client_with_tok_getter, user_id_getter):
    client_with_tok = client_with_tok_getter('user')
    user_id = user_id_getter('user')
    resp = client_with_tok.put('/api/users/{}'.format(user_id),
        data={
            'username': 'newusername',
        }
    )
    assert resp.status_code == 200


def test_logged_in_client_gets_correct_put_fields(
        client_with_tok_getter, user_id_getter):
    client_with_tok = client_with_tok_getter('user')
    user_id = user_id_getter('user')
    resp = client_with_tok.put('/api/users/{}'.format(user_id),
        data={
            'username': 'newusername',
        }
    )
    assert 'data' in resp.json
    assert {
        'user_id',
        'username',
        'signature',
        'roles',
        'avatar',
        'status',
        'n_posts',
        'n_topics',
        'created_at',
        'updated_at',
    } == set(resp.json['data'].keys())


def test_logged_in_client_corretly_edits_its_user(
        client_with_tok_getter, user_id_getter):
    client_with_tok = client_with_tok_getter('user')
    user_id = user_id_getter('user')
    resp_1 = client_with_tok.get('/api/users/{}'.format(user_id))
    resp_2 = client_with_tok.put('/api/users/{}'.format(user_id),
        data={
            'username': resp_1.json['data']['username'] + '_altered',
            'signature': resp_1.json['data']['signature'] + '_other',
        }
    )
    resp_3 = client_with_tok.get('/api/users/{}'.format(user_id))
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200
    assert resp_3.status_code == 200
    assert resp_3.json['data']['username'] \
        == resp_1.json['data']['username'] + '_altered'
    assert resp_3.json['data']['signature'] \
        == resp_1.json['data']['signature'] + '_other'


def test_logged_in_client_cannot_edit_user_referencing_nonexistent_avatar(
        client_with_tok_getter, user_id_getter):
    client_with_tok = client_with_tok_getter('user')
    user_id = user_id_getter('user')
    resp = client_with_tok.put('/api/users/{}'.format(user_id),
        data={
            'avatar_id': 999999,
        }
    )
    assert resp.status_code == 400


def test_logged_in_client_cannot_edit_other_user(
        client_with_tok_getter, user_id_getter):
    client_with_tok = client_with_tok_getter('user')
    other_user_id = user_id_getter('user_b')
    resp = client_with_tok.put('/api/users/{}'.format(other_user_id),
        data={
            'username': 'newusername',
        }
    )
    assert resp.status_code == 401


def test_logged_in_mod_cannot_edit_other_user(mod_with_tok, user_id_getter):
    other_user_id = user_id_getter('user_b')
    resp = mod_with_tok.put('/api/users/{}'.format(other_user_id),
        data={
            'username': 'newusername',
        }
    )
    assert resp.status_code == 401


def test_logged_in_admin_can_edit_other_user(admin_with_tok, user_id_getter):
    other_user_id = user_id_getter('user_b')
    resp = admin_with_tok.put('/api/users/{}'.format(other_user_id),
        data={
            'username': 'newusername',
        }
    )
    assert resp.status_code == 200


def test_client_can_get_user_posts(client, user_id):
    resp = client.get('/api/users/{}/posts'.format(user_id))
    assert resp.status_code == 200


def test_client_gets_correct_user_posts_fields(client, user_id):
    resp = client.get('/api/users/{}/posts'.format(user_id))
    assert 'offset' in resp.json
    assert resp.json['offset'] is None
    assert 'total' in resp.json
    assert 'data' in resp.json
    assert len(resp.json['data']) > 0
    assert resp.json['total'] == len(resp.json['data'])
    assert {
        'post_id',
        'created_at',
        'updated_at',
        'status',
        'content',
        'user',
        'topic',
    } == set(resp.json['data'][0].keys())


def test_client_can_get_user_topics(client, user_id):
    resp = client.get('/api/users/{}/topics'.format(user_id))
    assert resp.status_code == 200


def test_client_gets_correct_user_topics_fields(client, user_id):
    resp = client.get('/api/users/{}/topics'.format(user_id))
    assert 'offset' in resp.json
    assert resp.json['offset'] is None
    assert 'total' in resp.json
    assert 'data' in resp.json
    assert len(resp.json['data']) > 0
    assert resp.json['total'] == len(resp.json['data'])
    assert {
        'topic_id',
        'title',
        'status',
        'user',
        'subforum',
        'n_posts',
        'last_post',
        'created_at',
        'updated_at',
    } == set(resp.json['data'][0].keys())
