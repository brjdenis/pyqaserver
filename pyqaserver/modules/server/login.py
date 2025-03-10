import os
from flask import (Blueprint, request, render_template, flash,
                   redirect, url_for)
from flask_login import (login_user, login_required, logout_user, current_user,
                         AnonymousUserMixin)
from pyqaserver.models import db_general
from pyqaserver import site_config

cur_dir = site_config.FILE_DIR

login_bp = Blueprint('login', __name__,
                     template_folder=os.path.join(cur_dir, 'templates'),
                     static_folder=os.path.join(cur_dir, 'static', 'base'),
                     url_prefix="/login"
                     )


@login_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db_general.User.get_user(username)
        if user is None:
            flash('User not recognized. Try again.', 'danger')
        elif user.check_pass(password):
            login_user(user, remember=True)
            return redirect(url_for('login.menu'))
        else:
            flash('The password you entered is incorrect.', 'danger')
    return render_template('login.html')


@login_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return render_template('login.html')


@login_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile.html')


@login_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        username = current_user.username
        password = request.form["password"]
        db_general.User.change_pass(username, password)
    logout_user()
    return render_template('login.html')


@login_bp.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    return render_template('menu_page.html')


class AnonymousUser(AnonymousUserMixin):
    # Used for login during development
    def __init__(self):
        self.username = 'admin'
        self.display_name = 'admin'
