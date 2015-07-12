from flask import session, g
from plug_app import app

def build_user(row):
	if row:
		return dict(id=row[0], username=row[1], email=row[2], password=row[3])
	else:
		None

def find_current():
	if not session:
		return None
	cur = g.db.execute('select * from user where username=?', (session['username'],)).fetchone()
	user = build_user(cur)
	if user['password'] != session['password']: return None
	return user

def current_check(current, user_id):
	if current: return current['id'] == user_id
	return None