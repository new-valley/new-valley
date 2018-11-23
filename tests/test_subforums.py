import time


def test_client_can_get_subforums(client):
    resp = client.get('/api/subforums')
    assert resp.status_code == 200


def test_client_gets_correct_subforums_fields(client):
    resp = client.get('/api/subforums')
    assert 'offset' in resp.json
    assert resp.json['offset'] is None
    assert 'total' in resp.json
    assert 'data' in resp.json
    assert len(resp.json['data']) > 0
    assert resp.json['total'] == len(resp.json['data'])
    assert {
        'subforum_id',
        'created_at',
        'updated_at',
        'title',
        'description',
        'n_topics',
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
        'n_topics',
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
        'n_topics',
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


def test_client_can_get_subforum_topics(client, subforum_id):
    resp = client.get('/api/subforums/{}/topics'.format(subforum_id))
    assert resp.status_code == 200


def test_client_gets_correct_subforum_topics_fields(client, subforum_id):
    resp = client.get('/api/subforums/{}/topics'.format(subforum_id))
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
        'created_at',
        'updated_at',
    } == set(resp.json['data'][0].keys())


def test_logged_off_client_cannot_create_topic_in_subforum(
        client, subforum_id):
    resp = client.post('/api/subforums/{}/topics'.format(subforum_id))
    assert resp.status_code == 401


def test_logged_in_client_can_create_topic_in_subforum(
        client_with_tok, subforum_id):
    resp = client_with_tok.post(
        '/api/subforums/{}/topics'.format(subforum_id),
        data={
            'title': 'olar',
        }
    )
    assert resp.status_code == 200


def test_logged_in_client_gets_correct_n_topics(
        client_with_tok, subforum_id):
    resp_1 = client_with_tok.get('/api/me')
    resp_2 = client_with_tok.post(
        '/api/subforums/{}/topics'.format(subforum_id),
        data={
            'title': 'olar',
        }
    )
    resp_3 = client_with_tok.get('/api/me')
    resp_4 = client_with_tok.delete(
        '/api/topics/{}'.format(resp_2.json['data']['topic_id']))
    resp_5 = client_with_tok.get('/api/me')
    assert \
        resp_3.json['data']['n_topics'] == resp_1.json['data']['n_topics'] + 1
    assert \
        resp_5.json['data']['n_topics'] == resp_3.json['data']['n_topics'] - 1


def test_logged_in_client_gets_correct_fields_in_topic_creation(
        client_with_tok, subforum_id):
    resp = client_with_tok.post('/api/subforums/{}/topics'.format(subforum_id),
        data={
            'title': 'olar',
        }
    )
    assert {
        'topic_id',
        'title',
        'status',
        'user',
        'subforum',
        'n_posts',
        'created_at',
        'updated_at',
    } == set(resp.json['data'].keys())


def test_logged_in_client_correctly_creates_topic_in_subforum(
        client_with_tok, subforum_id):
    resp = client_with_tok.post('/api/subforums/{}/topics'.format(subforum_id),
        data={
            'title': 'olar',
        }
    )
    assert resp.json['data']['status'] == 'published'
    assert resp.json['data']['title'] == 'olar'
    assert resp.json['data']['subforum']['subforum_id'] == str(subforum_id)


def test_logged_in_client_under_antiflood_cannot_post_in_interval(
        client_with_tok_under_antifloood, antiflood_time, subforum_id):
    time.sleep(antiflood_time)
    start_time = time.time()
    resp_1 = client_with_tok_under_antifloood.post(
        '/api/subforums/{}/topics'.format(subforum_id),
        data={
            'title': 'olar',
        }
    )
    resp_2 = client_with_tok_under_antifloood.post(
        '/api/subforums/{}/topics'.format(subforum_id),
        data={
            'title': 'olar2',
        }
    )
    end_time = time.time()
    assert end_time - start_time < antiflood_time
    assert resp_1.status_code == 200
    assert resp_2.status_code == 429
