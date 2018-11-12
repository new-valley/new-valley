def test_client_can_get_subforums(client):
    resp = client.get('/api/subforums')
    assert resp.status_code == 200


def test_client_gets_correct_subforums_fields(client):
    resp = client.get('/api/subforums')
    assert 'offset' in resp.json
    assert resp.json['offset'] is None
    assert 'total' in resp.json
    assert 'data' in resp.json
    assert resp.json['total'] == len(resp.json['data'])
    assert {
        'subforum_id',
        'created_at',
        'updated_at',
        'title',
        'description',
        'position',
    } == set(resp.json['data'][0].keys())


def test_client_filters_subforums_fields(client):
    resp = client.get('/api/subforums?fields=title')
    subforums = resp.json['data']
    assert {
        'title',
    } == set(subforums[0].keys())


def test_client_offsets_subforums(client):
    resp_1 = client.get('/api/subforums')
    resp_2 = client.get('/api/subforums?offset=2')
    assert len(resp_1.json['data']) \
        == len(resp_2.json['data']) + min(2, len(resp_1.json['data']))
    

def test_client_limits_subforums(client):
    resp_1 = client.get('/api/subforums?max_n_results=1')
    resp_2 = client.get('/api/subforums?max_n_results=2')
    assert len(resp_1.json['data']) <= 1
    assert len(resp_2.json['data']) <= 2


def test_client_can_get_subforum(client, subforum_id):
    resp = client.get('/api/subforums/{}'.format(subforum_id))
    assert resp.status_code == 200
    assert 'data' in resp.json


def test_client_gets_correct_subforum_fields(client, subforum_id):
    resp = client.get('/api/subforums/{}'.format(subforum_id))
    assert 'data' in resp.json
    assert {
        'subforum_id',
        'created_at',
        'updated_at',
        'title',
        'description',
        'position',
    } == set(resp.json['data'].keys())


def test_logged_off_client_cannot_delete_subforum(client, subforum_id):
    resp = client.delete('/api/subforums/{}'.format(subforum_id))
    assert resp.status_code == 401


def test_logged_in_client_cannot_delete_subforum(client_with_tok, subforum_id):
    resp = client_with_tok.delete('/api/subforums/{}'.format(subforum_id))
    assert resp.status_code == 401


def test_logged_in_mod_cannot_delete_subforum(mod_with_tok, subforum_id):
    resp = mod_with_tok.delete('/api/subforums/{}'.format(subforum_id))
    assert resp.status_code == 401


def test_logged_in_admin_can_delete_subforum(admin_with_tok, subforum_id):
    resp = admin_with_tok.delete('/api/subforums/{}'.format(subforum_id))
    assert resp.status_code == 204


def test_logged_in_admin_corretly_deletes_subforum(admin_with_tok, subforum_id):
    resp_1 = admin_with_tok.get('/api/subforums/{}'.format(subforum_id))
    resp_2 = admin_with_tok.delete('/api/subforums/{}'.format(subforum_id))
    resp_3 = admin_with_tok.get('/api/subforums/{}'.format(subforum_id))
    assert resp_1.status_code == 200
    assert resp_2.status_code == 204
    assert resp_3.status_code == 404


def test_logged_off_client_cannot_edit_subforum(client, subforum_id):
    resp = client.put('/api/subforums/{}'.format(subforum_id),
        data={
            'title': 'updated',
        }
    )
    assert resp.status_code == 401


def test_logged_in_client_cannot_edit_subforum(client_with_tok, subforum_id):
    resp = client_with_tok.put('/api/subforums/{}'.format(subforum_id),
        data={
            'title': 'updated',
        }
    )
    assert resp.status_code == 401


def test_logged_in_mod_cannot_edit_subforum(mod_with_tok, subforum_id):
    resp = mod_with_tok.put('/api/subforums/{}'.format(subforum_id),
        data={
            'title': 'updated',
        }
    )
    assert resp.status_code == 401


def test_logged_in_admin_can_edit_subforum(admin_with_tok, subforum_id):
    resp = admin_with_tok.put('/api/subforums/{}'.format(subforum_id),
        data={
            'title': 'updated',
        }
    )
    assert resp.status_code == 200


def test_logged_in_admin_gets_correct_put_fields(admin_with_tok, subforum_id):
    resp = admin_with_tok.put('/api/subforums/{}'.format(subforum_id),
        data={
            'title': 'updated',
        }
    )
    assert 'data' in resp.json
    assert {
        'subforum_id',
        'created_at',
        'updated_at',
        'title',
        'description',
        'position',
    } == set(resp.json['data'].keys())


def test_logged_in_client_corretly_edits_subforum(admin_with_tok, subforum_id):
    resp_1 = admin_with_tok.get('/api/subforums/{}'.format(subforum_id))
    resp_2 = admin_with_tok.put('/api/subforums/{}'.format(subforum_id),
        data={
            'title': resp_1.json['data']['title'] + '_altered',
        }
    )
    resp_3 = admin_with_tok.get('/api/subforums/{}'.format(subforum_id))
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200
    assert resp_3.status_code == 200
    assert resp_3.json['data']['title'] \
        == resp_1.json['data']['title'] + '_altered'
