import pytest

from commands import generate_users
from db import mongo
from models import User


@pytest.fixture(scope='session')
def test_app():
    from app import create_app

    test_app = create_app('testing')
    context = test_app.app_context()
    context.push()

    yield test_app
    context.pop()


@pytest.fixture(scope='session')
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture(scope='function')
def create_test_db(test_client):
    generate_users.callback(3)
    test_client.test_user = User(**mongo.db.users.find_one())

    yield test_client
    mongo.db.command('dropDatabase')
