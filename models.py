import json
from flask import session
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, _id, name, email, bonus_card_id):
        self._id = _id
        self.name = name
        self.email = email
        self.bonus_card_id = bonus_card_id

    def __repr__(self):
        return f'<User(email={self.email})>'

    def get_id(self):
        return self._id

    @staticmethod
    def get_user_from_session():
        return User(
            **json.loads(session['user_json'])
        )
