from datetime import datetime, timedelta

from faker import Faker
from flask_wtf import FlaskForm
from flask import session
import wtforms as forms

from db import mongo
from schemas import UserSchema


class EmailForm(FlaskForm):

    email = forms.StringField('Email Address')

    def validate_email(form, field):
        email_validator = forms.validators.Email(
            message='That\'s not a valid email address.'
        )
        email_validator(form, field)

        found_user = mongo.db.users.find_one({'email': field.data})
        if not found_user:
            raise forms.ValidationError(
                f'User with email {field.data} not found'
            )

        session['user_json'] = UserSchema().dumps(found_user)

    def send_enter_code(self):
        fake = Faker()
        enter_code = fake.numerify('######')

        print(f'\nenter_code: {enter_code}\n')

        session['enter_code'] = enter_code
        session['enter_code_ttl'] = datetime.now() + timedelta(minutes=10)
        session['enter_code_block_expired_at'] = (
            datetime.now() + timedelta(minutes=1)
        )


class LogInByCodeForm(FlaskForm):

    enter_code = forms.StringField('Enter Code')

    def validate_enter_code(form, field):
        if datetime.now() > session['enter_code_ttl']:
            raise forms.ValidationError('Enter code is stale')

        if field.data != session['enter_code']:
            raise forms.ValidationError('Wrong enter code')

    def clean_session_data(self):
        del session['enter_code']
        del session['enter_code_ttl']
        del session['enter_code_block_expired_at']
