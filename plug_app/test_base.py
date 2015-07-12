import sqlite3
from flask.ext.testing import TestCase

from . import app
from contextlib import closing

def new_connect():
	return sqlite3.connect('test.db')

def new_init():
	with closing(new_connect()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

class BaseTestCase(TestCase):

	def create_app(self):
		app.config.from_object('config.TestConfiguration')
		return app

	def setUp(self):
		new_init()
		self.db = new_connect()

	def tearDown(self):
		if self.db is not None:
			self.db.close()

	def assert_flashes(self, expected_message, expected_category='message'):
		with self.client.session_transaction() as session:
			try:
				category, message = session['_flashes'][0]
			except KeyError:
				raise AssertionError('nothing flashed')
			assert expected_message in message
			assert expected_category == category

	def assert_data(self, response, message):
		self.assert_200(response)
		self.assertIn(message, response.data)