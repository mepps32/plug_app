import sqlite3
from plug_app import app
from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash

@app.route('/')
def main():
	return render_template('index.html')