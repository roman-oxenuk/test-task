from unittest.mock import patch

from db import mongo


API_URL = '/api/'


def test_transations_get(create_test_db):
    test_client = create_test_db

    url = API_URL + 'transactions/'

    def mock_current_user():
        return test_client.test_user

    with patch('flask_login.current_user', new_callable=mock_current_user):
        resp = test_client.get(url)

    expected_result = {
        'count': 0,
        'next': None,
        'objects': [],
        'prev': None,
        'total': 0
    }

    assert resp.status_code == 200
    assert expected_result == resp.json

    test_data = [
        {
            'transactions_id': 1,
            'bonus_card_id': test_client.test_user.bonus_card_id,
            'bonus_miles': 50,
            'flight_from': 'DME',
            'flight_to': 'LED',
            'flight_date': '2019-01-01'
        },
        {
            'transactions_id': 2,
            'bonus_card_id': test_client.test_user.bonus_card_id,
            'bonus_miles': 50,
            'flight_from': 'LED',
            'flight_to': 'DME',
            'flight_date': '2019-01-02'
        },
        {
            'transactions_id': 3,
            'bonus_card_id': test_client.test_user.bonus_card_id,
            'bonus_miles': 200,
            'flight_from': 'SVO',
            'flight_to': 'TJM',
            'flight_date': '2019-01-01'
        }
    ]
    mongo.db.transactions.insert_many(test_data)

    with patch('flask_login.current_user', new_callable=mock_current_user):
        resp = test_client.get(url)

    assert resp.status_code == 200
    resp_json = resp.json
    assert resp_json['count'] == 3
    assert resp_json['total'] == 3
    assert len(resp_json['objects']) == 3


def test_transations_post(create_test_db):
    test_client = create_test_db

    url = API_URL + 'transactions/'
    resp = test_client.post(url, json=[
        {
            'transactions_id': 1,
            'bonus_card_id': 1234,
            'bonus_miles': 50,
            'flight_from': 'DME',
            'flight_to': 'LED',
            'flight_date': '2019-01-01'
        }
    ])
    new_trans_id = str(mongo.db.transactions.find_one()['_id'])
    expected_result = [
        {
            '_id': new_trans_id,
            'transactions_id': 1,
            'bonus_card_id': 1234,
            'bonus_miles': 50,
            'flight_from': 'DME',
            'flight_to': 'LED',
            'flight_date': '2019-01-01'
        }
    ]
    assert resp.status_code == 201
    assert expected_result == resp.json

    # Check validation: incorrect data
    resp = test_client.post(
        url,
        json=[
            {
                'transactions_id': 1,
                'bonus_card_id': 1234,
                'bonus_miles': 50,
                'flight_from': 'DME',
                'flight_to': 'LED',
                'flight_date': '2019-01-41'
            }
        ]
    )
    expected_result = {
        '0': {'flight_date': ['flight_date must be a date in "%Y-%m-%d" format']}
    }
    assert resp.status_code == 400
    assert expected_result == resp.json

    # Check validation: same flight_from and flight_date
    resp = test_client.post(
        url,
        json=[
            {
                'transactions_id': 1,
                'bonus_card_id': 1234,
                'bonus_miles': 50,
                'flight_from': 'DME',
                'flight_to': 'DME',
                'flight_date': '2019-01-01'
            }
        ]
    )
    expected_result = {
        '_schema': ['Fields "flight_from" and "flight_to" can not have the same value']
    }
    assert resp.status_code == 400
    assert expected_result == resp.json
