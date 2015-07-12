import os
_basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfiguration(object):
	DEBUG = True
	ADMINS = frozenset(['mepps32@gmail.com'])
	SECRET_KEY = 'super secret key'

	DATABASE = os.path.join(_basedir, 'plug.db')

	THREADS_PER_PAGE = 8

	CSRF_ENABLED = True
	CSRF_SESSION_KEY = "somethingimpossibletoguess"

class TestConfiguration(BaseConfiguration):
	DEBUG = False

	DATABASE = os.path.join(_basedir, 'test.db')

	CSRF_ENABLED = False