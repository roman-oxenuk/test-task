from datetime import datetime

from flask import Blueprint, render_template, session, url_for, redirect, flash
from flask_login import login_required, login_user, logout_user

from forms import EmailForm, LogInByCodeForm
from models import User


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    email_form = EmailForm()

    enter_code_block_expired_at = session.get('enter_code_block_expired_at')
    if enter_code_block_expired_at and datetime.now() < enter_code_block_expired_at:
        seconds_to_wait = (enter_code_block_expired_at - datetime.now()).seconds

        err_msg = f'Please wait {seconds_to_wait} seconds before create a new enter code'
        email_form.email.errors = [err_msg]

        return render_template('auth/login.html', form=email_form)

    if email_form.validate_on_submit():
        email_form.send_enter_code()
        return redirect(url_for('.login_by_code'))

    return render_template('auth/login.html', form=email_form)


@bp.route('/login_by_code', methods=('GET', 'POST'))
def login_by_code():
    login_form = LogInByCodeForm()
    if login_form.validate_on_submit():
        login_user(User.get_user_from_session())
        login_form.clean_session_data()
        return redirect('/api/transactions')

    return render_template('auth/login_by_code.html', form=login_form)


@bp.route('/logout', methods=('GET',))
@login_required
def logout():
    logout_user()
    flash('You are unlogged')
    return redirect(url_for('.login'))
