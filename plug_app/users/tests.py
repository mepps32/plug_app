from flask import url_for
from helper import *

from plug_app.test_base import BaseTestCase

class UserViewTests(BaseTestCase):

	def create_user(self):
		self.db.execute('''insert into user (username, email, password)
						values (?, ?, ?)''', ("user1", 'email@email.com', "password"))
		self.db.commit()

	def create_user1(self):
		self.db.execute('''insert into user (username, email, password)
						values (?, ?, ?)''', ("user", 'user@email.com', "1234"))
		self.db.commit()

	def assert_db(self, response, username, email, password):
		cur = self.db.execute('select * from user where username=?', (username,)).fetchone()
		user = build_user(cur)
		assert password == user['password']
		assert email == user['email']
	
	def assert_db_wrong(self, response, username, email, password):
		cur = self.db.execute('select * from user where username=?', (username,)).fetchone()
		user = build_user(cur)
		assert user == None

	def assert_db_all(self, response, length):
		cur = self.db.execute('select * from user').fetchall()
		users = [build_user(user) for user in cur]
		assert len(users) == length

	def assert_user_session(self, username, password):
		with self.client.session_transaction() as session:
			try:
				sess_name = session['username']
				sess_pass = session['password']
			except KeyError:
				raise AssertionError('no user session')
			assert username == sess_name
			assert password == sess_pass

	def test_user_login_logout(self):
		self.create_user()
		response = self.client.post(url_for('login'), data=dict(
			username="user1",
			password="password"
		))
		cur = self.db.execute('select * from user where username=?', ("user1",)).fetchone()
		user = build_user(cur)
		self.assert_status(response, 302)
		self.assert_redirects(response, url_for('show_user', user_id=user['id']))
		self.assert_user_session('user1', 'password')
		response = self.client.get(url_for('logout'))
		self.assert_status(response, 302)
		self.assert_redirects(response, url_for('show_users'))

	def test_invalid_password(self):
		self.create_user()

		with self.client as c:
			response = c.post(url_for('login'),
										data=dict(
											username="user1",
											password="pass"
										))
			self.assert_200(response)
			self.assertIn("Invalid password", response.data)
	
	def test_invalid_username(self):
		self.create_user()

		with self.client as c:
			response = c.post(url_for('login'),
										data=dict(
											username="user",
											password="pass"
										))
			self.assert_200(response)
			self.assertIn("Invalid username", response.data)

	def test_invalid_everything(self):
		self.create_user()

		with self.client as c:
			response = c.post(url_for('login'),
										data=dict(
											username='1234',
											password='1234'
										))
			self.assert_data(response, "Invalid username")

	def test_gets_not_logged_in(self):
		self.create_user()
		response = self.client.get(url_for('show_users'))
		self.assert_status(response, 200)
		response = self.client.get(url_for('show_user', user_id=1))
		self.assert_data(response, "You are not logged in.")
		response = self.client.get(url_for('edit_user', user_id=1))
		self.assert_data(response, "Sorry, you can't edit anything.")
		response = self.client.get(url_for('delete_user', user_id=1))
		self.assert_data(response, "Sorry, you can't.")

	def test_gets_logged_in(self):
		self.create_user()
		self.client.post(url_for('login'), data=dict(
			username="user1",
			password="password"
		))
		response = self.client.get(url_for('show_users'))
		self.assert_200(response)
		response = self.client.get(url_for('show_user', user_id=1))
		self.assert_200(response)
		self.assert_data(response, "None. You are the current user.")
		response = self.client.get(url_for('edit_user', user_id=1))
		self.assert_data(response, "Username:")
		response = self.client.get(url_for('delete_user', user_id=1))
		self.assert_data(response, 'value="Delete"')

	def test_gets_logged_in_diff(self):
		self.create_user()
		self.create_user1()
		self.client.post(url_for('login'), data=dict(
			username="user1",
			password="password"
		))
		response = self.client.get(url_for('show_users'))
		self.assert_200(response)
		self.assert_data(response, "Nothing to see here.")
		self.assert_data(response, "password")
		response = self.client.get(url_for('show_user', user_id=1))
		self.assert_200(response)
		self.assert_data(response, "None. You are the current user.")
		response = self.client.get(url_for('edit_user', user_id=1))
		self.assert_data(response, "Username:")
		response = self.client.get(url_for('delete_user', user_id=1))
		self.assert_data(response, 'value="Delete"')
		response = self.client.get(url_for('show_user', user_id=2))
		self.assert_data(response, "Sorry, you can't see anything.")
		response = self.client.get(url_for('edit_user', user_id=2))
		self.assert_data(response, "Sorry, you can't edit anything.")
		response = self.client.get(url_for('delete_user', user_id=2))
		self.assert_data(response, "Sorry, you can't.")

	def test_create_user(self):
		response = self.client.post(url_for('new_user'),
									data=dict(
										username='users',
										password="pass",
										email="fake@email.com"
									))
		self.assert_status(response, 302)
		self.assert_redirects(response, url_for('show_user', user_id=1))
		self.assert_db(response, 'users', 'fake@email.com', 'pass')

	def test_create_user_wrong(self):
		response = self.client.post(url_for('new_user'),
									data=dict(
										username='users',
										password="pass",
										email="fake@email.com"
									))
		self.assert_status(response, 302)
		self.assert_redirects(response, url_for('show_user', user_id=1))
		self.assert_db_wrong(response, 'use', 'fake@email.com', 'pass')

	def test_edit_user(self):
		self.create_user()
		self.client.post(url_for('login'), data=dict(
			username="user1",
			password="password"
		))
		response = self.client.post(url_for('edit_user', user_id=1),
									data=dict(
										username='users',
										password="pass",
										email="fake@email.com"
									))
		self.assert_status(response, 302)
		self.assert_redirects(response, url_for('show_user', user_id=1))
		self.assert_db(response, 'users', 'fake@email.com', 'pass')

	def test_edit_user_wrong(self):
		self.create_user()
		response = self.client.post(url_for('edit_user', user_id=1),
									data=dict(
										username='users',
										password="pass",
										email="fake@email.com"
									))
		self.assert_status(response, 302)
		self.assert_redirects(response, url_for('show_users'))
		self.assert_status(response, 302)
		self.assert_flashes("Sorry, you have no permission to edit user.")
		self.assert_db_wrong(response, 'use', 'fake@email.com', 'pass')

	def test_delete_user(self):
		self.create_user()
		self.client.post(url_for('login'), data=dict(
			username="user1",
			password="password"
		))
		response = self.client.post(url_for('delete_user', user_id=1))
		self.assert_status(response, 302)
		self.assert_redirects(response, url_for('show_users'))
		self.assert_db_all(response, 0)

	def test_delete_user_wrong(self):
		self.create_user()
		response = self.client.post(url_for('delete_user', user_id=1))
		self.assert_status(response, 302)
		self.assert_redirects(response, url_for('show_users'))
		self.assert_status(response, 302)
		self.assert_flashes("Sorry, you have no permission to delete user.")
		self.assert_db_all(response, 1)
