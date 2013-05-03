from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'users'
	name = db.Column(db.String(40))
	email = db.Column(db.String(40))
	auto_add = db.Column(db.Boolean)
	carrier = db.Column(db.Integer)
	remind_type = db.Column(db.Integer)
	post_by_default = db.Column(db.Boolean)
	post_time = db.Column(db.Integer)
	fb_id = db.Column(db.Integer, primary_key=True)

	def __init__(self, name, email, fb_id):
		self.name = name
		self.email = email
		self.fb_id = fb_id

class Reminder(db.Model):
	__tablename__ = 'reminders'
	send_time = db.Column(db.DateTime)
	reminder_id = db.Column(db.Integer, primary_key=True)
	event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.fb_id'))
	type = db.Column(db.Integer)
	
class Event(db.Model):
	__tablename__ = 'events'
	title = db.Column(db.String(40))
	description = db.Column(db.String(800))
	uid = db.Column(db.Integer, db.ForeignKey('user.fb_id'))
	event_id  = db.Column(db.Integer, primary_key=True)

	def __init__(self, title, description, uid, event_id):
		self.title = title
		self.description = description
		self.uid = uid
		self.event_id = event_id


