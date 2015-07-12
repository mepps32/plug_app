import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash
from plug_app import app
from helper import *

@app.route('/user/')
def show_users():
	error = None
	current_user = None
	cur = g.db.execute('select * from user').fetchall()
	users = [build_user(row) for row in cur]

	current_user = find_current()

	if not current_user:
		error = "You are not logged in."

	return render_template('users.html', users=users, error=error, current_user=current_user)

@app.route('/user/<int:user_id>/')
def show_user(user_id):
	cur = g.db.execute('select * from user where id=?', (user_id,)).fetchone()
	user = build_user(cur)
	error = None

	current_user = find_current()

	if not current_user:
		error = "You are not logged in."
	elif current_check(current_user, user_id):
		error = "None. You are the current user."
	else:
		error = "You are not the current user."
	
	current_user = current_check(current_user, user_id) and current_user

	return render_template('user.html', user=user, error=error, current_user=current_user)

@app.route('/user/new/', methods=['GET', 'POST'])
def new_user():
	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']

		if username and email and password:
			g.db.execute('''insert into user (username, email, password)
							values (?, ?, ?)''', (username, email, password))
			g.db.commit()

			cur = g.db.execute('select * from user where username=?', (username,)).fetchone()
			user = build_user(cur)

			session['username'] = username
			session['password'] = password
			return redirect(url_for('show_user', user_id=user['id']))

		flash("Aren't you missing something?")
		return render_template('new_user.html', username=username, email=email)
	return render_template('new_user.html', username="", email="")

@app.route('/user/<int:user_id>/edit/', methods=['GET', 'POST'])
def edit_user(user_id):
	cur = g.db.execute('select * from user where id=?', (user_id,)).fetchone()
	user = build_user(cur)
	error = None

	current_user = find_current()

	if not current_user:
		error = "You are not logged in."
	elif current_check(current_user, user_id):
		error = "None. You are the current user."
	else:
		error = "You are not the current user."
	
	current_user = current_check(current_user, user_id) and current_user

	if request.method == 'POST':
		if current_user:
			username = request.form['username'] or user['username']
			email = request.form['email'] or user['email']
			password = request.form['password'] or user['password']

			g.db.execute('''UPDATE user SET username=?, email=?, password=? WHERE id=?''', (username, email, password, user['id']))
			g.db.commit()

			session['username'] = username
			session['password'] = password

			return redirect(url_for('show_user', user_id=user['id']))
		else:
			flash("Sorry, you have no permission to edit user.")
			return redirect(url_for('show_users'))
	return render_template('edit_user.html', user=user, error=error, current_user=current_user)

@app.route('/user/<int:user_id>/delete/', methods=['GET', 'POST'])
def delete_user(user_id):
	cur = g.db.execute('select * from user where id=?', (user_id,)).fetchone()
	user = build_user(cur)
	error = None

	current_user = find_current()

	if not current_user:
		error = "You are not logged in."
	elif current_check(current_user, user_id):
		error = "None. You are the current user."
	else:
		error = "You are not the current user."

	current_user = current_check(current_user, user_id) and current_user

	if request.method == "POST":
		if current_user:
			g.db.execute('DELETE FROM user WHERE id=?', (user_id,))
			g.db.commit()
			session.pop('username', None)
			session.pop('password', None)
		else:
			flash("Sorry, you have no permission to delete user.")
		return redirect(url_for('show_users'))
	return render_template('delete_user.html', user=user, error=error, current_user=current_user)

@app.route('/login/', methods=['GET','POST'])
def login():
	error = None

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		cur = g.db.execute('SELECT * FROM user WHERE username=?', (username,)).fetchone()
		user = build_user(cur)
		if not user:
			error = "Invalid username"
		elif password != user['password']:
			error = 'Invalid password'
		else:
			session['username'] = username
			session['password'] = password
			return redirect(url_for('show_user', user_id=user['id']))

	return render_template('login.html', error=error)

@app.route('/logout/')
def logout():
	session.pop('username', None)
	session.pop('password', None)
	return redirect(url_for('show_users'))