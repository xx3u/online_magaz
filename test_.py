import json
import pytest
from lxml import html
from io import StringIO
from unittest import mock
from hello import app


@pytest.fixture
def client():
    client = app.test_client()
    return client


@pytest.fixture
def db_data():
    cart = {
        'banana': 5,
        'grapes': 100
    }
    return StringIO(json.dumps(cart))


def test_index(client):
    response = client.get('/')
    response = response.data.decode('utf-8')
    assert 'Welcome to Online Shop "Alashopkz"!' in response


def test_post_items_update(client, db_data):
    with mock.patch('hello.open') as mocked:
        mocked.return_value = db_data
        response = client.post(
            '/items',
            data={
                'banana_name': 'banana',
                'banana_quantity': 5,
                'grapes_name': 'apple',
                'grapes_quantity': 100
            }
        )
        response = response.data.decode('utf-8')
        assert '<input type="text" value="banana" name="banana_name">' \
            in response
        assert '<input type="text" value="5" name="banana_quantity">' \
            in response
        assert '<input type="text" value="apple" name="apple_name">' \
            in response
        assert '<input type="text" value="100" name="apple_quantity">' \
            in response


def test_post_items_remove(client, db_data):
    with mock.patch('hello.open') as mocked:
        mocked.return_value = db_data
        response = client.post(
            '/items', data={
                'banana_name': 'banana',
                'banana_quantity': 5,
                'grapes_name': 'grapes',
                'grapes_quantity': 100,
                'grapes_delete': 'on'
            }
        )
        response = response.data.decode('utf-8')
        assert '<input type="text" value="banana" name="banana_name">' \
            in response
        assert '<input type="text" value="5" name="banana_quantity">' \
            in response
        assert 'grapes' not in response


def test_post_items_add(client, db_data):
    with mock.patch('hello.open') as mocked:
        mocked.return_value = db_data
        response = client.post(
            '/items',
            data={
                'add': ''
            }
        )
        response = response.data.decode('utf-8')
        response = html.fromstring(response)
        assert len(response.cssselect('input[name="__name"]')) == 1
        assert len(response.cssselect('input[name="__quantity"]')) == 1
