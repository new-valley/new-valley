import time


def test_client_can_get_topics(client):
    resp = client.get('/api/topics')
    assert resp.status_code == 200


def test_client_gets_correct_topics_fields(client):
    resp = client.get('/api/topics')
    assert 'offset' in resp.json
    assert resp.json['offset'] is None
    assert 'total' in resp.json
    assert 'data' in resp.json
    assert resp.json['total'] == len(resp.json['data'])
    assert {
        'topic_id',
        'title',
        'status',
        'user',
        'subforum',
        'created_at',
        'updated_at',
    } == set(resp.json['data'][0].keys())


def test_client_filters_topics_fields(client):
    resp = client.get('/api/topics?fields=topic_id,user,title')
    topics = resp.json['data']
    assert {
        'topic_id',
        'user',
        'title',
    } == set(topics[0].keys())


def test_client_offsets_topics(client):
    resp_1 = client.get('/api/topics')
    resp_2 = client.get('/api/topics?offset=2')
    assert len(resp_1.json['data']) \
        == len(resp_2.json['data']) + min(2, len(resp_1.json['data']))
    

def test_client_limits_topics(client):
    resp_1 = client.get('/api/topics?max_n_results=1')
    resp_2 = client.get('/api/topics?max_n_results=2')
    assert len(resp_1.json['data']) <= 1
    assert len(resp_2.json['data']) <= 2


def test_client_can_get_topic(client, topic_id):
    resp = client.get('/api/topics/{}'.format(topic_id))
    assert resp.status_code == 200
    assert 'data' in resp.json


def test_client_gets_correct_topic_fields(client, topic_id):
    resp = client.get('/api/topics/{}'.format(topic_id))
    assert 'data' in resp.json
    assert {
        'topic_id',
        'title',
        'status',
        'user',
        'subforum',
        'created_at',
        'updated_at',
    } == set(resp.json['data'].keys())


def test_logged_off_client_cannot_delete_topic(client, topic_id):
    resp = client.delete('/api/topics/{}'.format(topic_id))
    assert resp.status_code == 401


def test_logged_in_client_cannot_delete_other_users_topic(
        client_with_tok_getter, topic_id_getter):
    client_with_tok = client_with_tok_getter('user')
    other_user_topic_id = topic_id_getter('user_b')
    resp = client_with_tok.delete('/api/topics/{}'.format(other_user_topic_id))
    assert resp.status_code == 401


def test_logged_in_client_can_delete_their_topic(
        client_with_tok_getter, topic_id_getter):
    client_with_tok = client_with_tok_getter('user')
    user_topic_id = topic_id_getter('user')
    resp = client_with_tok.delete('/api/topics/{}'.format(user_topic_id))
    assert resp.status_code == 204


def test_logged_in_mod_can_delete_topic(mod_with_tok, topic_id):
    resp = mod_with_tok.delete('/api/topics/{}'.format(topic_id))
    assert resp.status_code == 204


def test_logged_in_admin_can_delete_topic(admin_with_tok, topic_id):
    resp = admin_with_tok.delete('/api/topics/{}'.format(topic_id))
    assert resp.status_code == 204


def test_logged_in_admin_corretly_deletes_topic(admin_with_tok, topic_id):
    resp_1 = admin_with_tok.get('/api/topics/{}'.format(topic_id))
    resp_2 = admin_with_tok.delete('/api/topics/{}'.format(topic_id))
    resp_3 = admin_with_tok.get('/api/topics/{}'.format(topic_id))
    assert resp_1.status_code == 200
    assert resp_2.status_code == 204
    assert resp_3.status_code == 404


def test_logged_off_client_cannot_edit_topic(client, topic_id):
    resp = client.put('/api/topics/{}'.format(topic_id),
        data={
            'title': 'updated',
        }
    )
    assert resp.status_code == 401


def test_logged_in_client_cannot_edit_other_users_topic(
        client_with_tok_getter, topic_id_getter):
    client_with_tok = client_with_tok_getter('user')
    other_user_topic_id = topic_id_getter('user_b')
    resp = client_with_tok.put('/api/topics/{}'.format(other_user_topic_id),
        data={
            'title': 'updated',
        }
    )
    assert resp.status_code == 401


def test_logged_in_client_can_edit_their_topic(
        client_with_tok_getter, topic_id_getter):
    client_with_tok = client_with_tok_getter('user')
    user_topic_id = topic_id_getter('user')
    resp = client_with_tok.put('/api/topics/{}'.format(user_topic_id),
        data={
            'title': 'updated',
        }
    )
    assert resp.status_code == 200


def test_logged_in_mod_can_edit_topic(mod_with_tok, topic_id):
    resp = mod_with_tok.put('/api/topics/{}'.format(topic_id),
        data={
            'title': 'updated',
        }
    )
    assert resp.status_code == 200


def test_logged_in_admin_can_edit_topic(admin_with_tok, topic_id):
    resp = admin_with_tok.put('/api/topics/{}'.format(topic_id),
        data={
            'title': 'updated',
        }
    )
    assert resp.status_code == 200


def test_logged_in_client_gets_correct_put_fields(
        client_with_tok_getter, topic_id_getter):
    client_with_tok = client_with_tok_getter('user')
    topic_id = topic_id_getter('user')
    resp = client_with_tok.put('/api/topics/{}'.format(topic_id),
        data={
            'title': 'new',
        }
    )
    assert 'data' in resp.json
    assert {
        'topic_id',
        'title',
        'status',
        'user',
        'subforum',
        'created_at',
        'updated_at',
    } == set(resp.json['data'].keys())


def test_logged_in_client_corretly_edits_its_topic(
        client_with_tok_getter, topic_id_getter):
    client_with_tok = client_with_tok_getter('user')
    topic_id = topic_id_getter('user')
    resp_1 = client_with_tok.get('/api/topics/{}'.format(topic_id))
    resp_2 = client_with_tok.put('/api/topics/{}'.format(topic_id),
        data={
            'title': resp_1.json['data']['title'] + '_altered',
        }
    )
    resp_3 = client_with_tok.get('/api/topics/{}'.format(topic_id))
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200
    assert resp_3.status_code == 200
    assert resp_3.json['data']['title'] \
        == resp_1.json['data']['title'] + '_altered'


def test_client_can_get_topic_posts(client, topic_id):
    resp = client.get('/api/topics/{}/posts'.format(topic_id))
    assert resp.status_code == 200


def test_client_gets_correct_topic_posts_fields(client, topic_id):
    resp = client.get('/api/topics/{}/posts'.format(topic_id))
    assert 'offset' in resp.json
    assert resp.json['offset'] is None
    assert 'total' in resp.json
    assert 'data' in resp.json
    assert len(resp.json['data']) > 0
    assert resp.json['total'] == len(resp.json['data'])
    assert {
        'post_id',
        'topic',
        'user',
        'content',
        'status',
        'created_at',
        'updated_at',
    } == set(resp.json['data'][0].keys())


def test_logged_off_client_cannot_create_post_in_topic(client, topic_id):
    resp = client.post('/api/topics/{}/posts'.format(topic_id))
    assert resp.status_code == 401


def test_logged_in_client_can_create_post_in_topic(client_with_tok, topic_id):
    resp = client_with_tok.post('/api/topics/{}/posts'.format(topic_id),
        data={
            'content': 'olar',
        }
    )
    assert resp.status_code == 200


def test_logged_in_client_gets_correct_fields_in_post_creation(
        client_with_tok, topic_id):
    resp = client_with_tok.post('/api/topics/{}/posts'.format(topic_id),
        data={
            'content': 'olar',
        }
    )
    assert {
        'post_id',
        'topic',
        'user',
        'content',
        'status',
        'created_at',
        'updated_at',
    } == set(resp.json['data'].keys())


def test_logged_in_client_correctly_creates_post_in_topic(
        client_with_tok, topic_id):
    resp = client_with_tok.post('/api/topics/{}/posts'.format(topic_id),
        data={
            'content': 'olar',
        }
    )
    assert resp.json['data']['status'] == 'published'
    assert resp.json['data']['content'] == 'olar'
    assert resp.json['data']['topic']['topic_id'] == str(topic_id)


def test_logged_in_client_under_antiflood_cannot_post_in_interval(
        client_with_tok_under_antifloood, antiflood_time, topic_id):
    time.sleep(antiflood_time)
    start_time = time.time()
    resp_1 = client_with_tok_under_antifloood.post(
        '/api/topics/{}/posts'.format(topic_id),
        data={
            'content': 'olar',
        }
    )
    resp_2 = client_with_tok_under_antifloood.post(
        '/api/topics/{}/posts'.format(topic_id),
        data={
            'content': 'olar2',
        }
    )
    end_time = time.time()
    assert end_time - start_time < antiflood_time
    assert resp_1.status_code == 200
    assert resp_2.status_code == 429
