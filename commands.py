import click
from click import BadParameter
from faker import Faker
import marshmallow as ma

from db import mongo


fake = Faker()


@click.command('create_indexes')
def create_indexes():
    '''Add indexes to collections'''
    mongo.db.create_collection('users')
    mongo.db.users.create_index('email', unique=True)

    mongo.db.create_collection('transactions')
    mongo.db.transactions.create_index('bonus_card_id')


@click.command('generate_users')
@click.argument('amount')
def generate_users(amount):
    '''Generate fake users'''
    amount = int(amount)

    fake_users = []
    for ind in range(amount):
        name = fake.name()
        email_name = name.replace(' ', '.').lower()
        email_domain = fake.free_email_domain()
        fake_user = {
            'name': name,
            'email': f'{email_name}@{email_domain}',
            'bonus_card_id': fake.numerify('######')
        }
        fake_users.append(fake_user)

    result = mongo.db.users.insert_many(fake_users, ordered=True)
    for ind, inserted_id in enumerate(result.inserted_ids):
        fake_users[ind]['_id'] = inserted_id

    ma.pprint(fake_users, indent=4)


def fake_airports_codes():
    unique_codes = set([])
    for ind in range(100):
        unique_codes.add(
            fake.lexify('???').upper()
        )
    return unique_codes


AIRPORTS_CODES = fake_airports_codes()


@click.command('generate_transaction_for_user')
@click.argument('user_email')
@click.argument('amount')
def generate_transaction_for_user(user_email, amount):
    '''Generate transaction for given user'''
    amount = int(amount)
    user = mongo.db.users.find_one({'email': user_email})

    if not user:
        raise BadParameter(f'User with email {user_email} not found')

    fake_transactions = []
    for ind in range(amount):
        airports = fake.random_sample(AIRPORTS_CODES, 2)
        fake_transaction = {
            'transactions_id': fake.numerify('########'),
            'bonus_card_id': user['bonus_card_id'],
            'bonus_miles': fake.pyint(min_value=0, max_value=100),
            'flight_from': airports[0],
            'flight_to': airports[1],
            'flight_date': ma.utils.to_iso_date(
                fake.date_between(start_date='-10y', end_date='today')
            )
        }
        fake_transactions.append(fake_transaction)

    result = mongo.db.transactions.insert_many(fake_transactions, ordered=True)
    for ind, inserted_id in enumerate(result.inserted_ids):
        fake_transactions[ind]['_id'] = inserted_id

    ma.pprint(fake_transactions, indent=4)
