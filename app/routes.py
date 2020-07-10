from flask import render_template, flash, redirect
from app import flask_app
from app.forms import LoginForm

@flask_app.route('/')
@flask_app.route('/index')
def index():
    user = {'username': 'bob'}
    posts = [
        {
            'author': {'username': 'Jan Huss'},
            'body': 'I like stuff'
        },
        {
            'author': {'username': 'Suzerain'},
            'body': 'Things are cool'
        },
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
