def test_client_can_get_posts(client):
    resp = client.get('/api/posts')
    assert resp.status_code == 200


def test_client_gets_correct_posts_fields(client):
    resp = client.get('/api/posts')
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


def test_client_filters_posts_fields(client):
    resp = client.get('/api/posts?fields=post_id,user,status')
    posts = resp.json['data']
    assert {
        'post_id',
        'user',
        'status',
    } == set(posts[0].keys())


def test_client_offsets_posts(client):
    resp_1 = client.get('/api/posts')
    resp_2 = client.get('/api/posts?offset=2')
    assert len(resp_1.json['data']) \
        == len(resp_2.json['data']) + min(2, len(resp_1.json['data']))
    

def test_client_limits_posts(client):
    resp_1 = client.get('/api/posts?max_n_results=1')
    resp_2 = client.get('/api/posts?max_n_results=2')
    assert len(resp_1.json['data']) <= 1
    assert len(resp_2.json['data']) <= 2


def test_client_can_get_post(client, post_id):
    resp = client.get('/api/posts/{}'.format(post_id))
    assert resp.status_code == 200
    assert 'data' in resp.json


def test_client_gets_correct_post_fields(client, post_id):
    resp = client.get('/api/posts/{}'.format(post_id))
    assert 'data' in resp.json
    assert {
        'post_id',
        'created_at',
        'updated_at',
        'status',
        'content',
        'user',
        'topic',
    } == set(resp.json['data'].keys())


def test_logged_off_client_cannot_delete_post(client, post_id):
    resp = client.delete('/api/posts/{}'.format(post_id))
    assert resp.status_code == 401


def test_logged_in_client_cannot_delete_other_users_post(
        client_with_tok_getter, post_id_getter):
    client_with_tok = client_with_tok_getter('user')
    other_user_post_id = post_id_getter('user_b')
    resp = client_with_tok.delete('/api/posts/{}'.format(other_user_post_id))
    assert resp.status_code == 401


def test_logged_in_client_can_delete_their_post(
        client_with_tok_getter, post_id_getter):
    client_with_tok = client_with_tok_getter('user')
    user_post_id = post_id_getter('user')
    resp = client_with_tok.delete('/api/posts/{}'.format(user_post_id))
    assert resp.status_code == 204


def test_logged_in_mod_can_delete_post(mod_with_tok, post_id):
    resp = mod_with_tok.delete('/api/posts/{}'.format(post_id))
    assert resp.status_code == 204


def test_logged_in_admin_can_delete_post(admin_with_tok, post_id):
    resp = admin_with_tok.delete('/api/posts/{}'.format(post_id))
    assert resp.status_code == 204


def test_logged_in_admin_corretly_deletes_post(admin_with_tok, post_id):
    resp_1 = admin_with_tok.get('/api/posts/{}'.format(post_id))
    resp_2 = admin_with_tok.delete('/api/posts/{}'.format(post_id))
    resp_3 = admin_with_tok.get('/api/posts/{}'.format(post_id))
    assert resp_1.status_code == 200
    assert resp_2.status_code == 204
    assert resp_3.status_code == 404


def test_logged_off_client_cannot_edit_post(client, post_id):
    resp = client.put('/api/posts/{}'.format(post_id),
        data={
            'content': 'updated',
        }
    )
    assert resp.status_code == 401


def test_logged_in_client_cannot_edit_other_users_post(
        client_with_tok_getter, post_id_getter):
    client_with_tok = client_with_tok_getter('user')
    other_user_post_id = post_id_getter('user_b')
    resp = client_with_tok.put('/api/posts/{}'.format(other_user_post_id),
        data={
            'content': 'updated',
        }
    )
    assert resp.status_code == 401


def test_logged_in_client_can_edit_their_post(
        client_with_tok_getter, post_id_getter):
    client_with_tok = client_with_tok_getter('user')
    user_post_id = post_id_getter('user')
    resp = client_with_tok.put('/api/posts/{}'.format(user_post_id),
        data={
            'content': 'updated',
        }
    )
    assert resp.status_code == 200


def test_logged_in_mod_can_edit_post(mod_with_tok, post_id):
    resp = mod_with_tok.put('/api/posts/{}'.format(post_id),
        data={
            'content': 'updated',
        }
    )
    assert resp.status_code == 200


def test_logged_in_admin_can_edit_post(admin_with_tok, post_id):
    resp = admin_with_tok.put('/api/posts/{}'.format(post_id),
        data={
            'content': 'updated',
        }
    )
    assert resp.status_code == 200


def test_logged_in_client_gets_correct_put_fields(
        client_with_tok_getter, post_id_getter):
    client_with_tok = client_with_tok_getter('user')
    post_id = post_id_getter('user')
    resp = client_with_tok.put('/api/posts/{}'.format(post_id),
        data={
            'content': 'new',
        }
    )
    assert 'data' in resp.json
    assert {
        'post_id',
        'created_at',
        'updated_at',
        'status',
        'content',
        'user',
        'topic',
    } == set(resp.json['data'].keys())


def test_logged_in_client_corretly_edits_its_post(
        client_with_tok_getter, post_id_getter):
    client_with_tok = client_with_tok_getter('user')
    post_id = post_id_getter('user')
    resp_1 = client_with_tok.get('/api/posts/{}'.format(post_id))
    resp_2 = client_with_tok.put('/api/posts/{}'.format(post_id),
        data={
            'content': resp_1.json['data']['content'] + '_altered',
        }
    )
    resp_3 = client_with_tok.get('/api/posts/{}'.format(post_id))
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200
    assert resp_3.status_code == 200
    assert resp_3.json['data']['content'] \
        == resp_1.json['data']['content'] + '_altered'
