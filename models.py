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
	carrier = db.Column(db.BigInteger)
	remind_type = db.Column(db.BigInteger)
	phone = db.Column(db.BigInteger)
	remind_by_default = db.Column(db.Boolean)
	reminder_time = db.Column(db.BigInteger)
	post_by_default = db.Column(db.Boolean)
	post_time = db.Column(db.BigInteger)
	google_cred = db.Column(db.String(300))
	fb_id = db.Column(db.BigInteger, primary_key=True)
	default_calendar = db.Column(db.BigInteger)
	access_token = db.Column(db.String(200))
	google_cred = db.Column(db.String(1000))
	def __init__(self, name, email, fb_id):
		self.name = name
		self.email = email
		self.fb_id = fb_id
		self.remind_type = 0
		self.post_by_default = True
		self.remind_by_default = True
		self.reminder_time = 30
		self.post_time = 30
		self.phone = 5555555555
		self.carrier = 0
		self.auto_add = True
		self.reminder_time = 30

class Reminder(db.Model):
	__tablename__ = 'reminders'
	send_time = db.Column(db.DateTime)
	reminder_id = db.Column(db.BigInteger, primary_key=True)
	event_id = db.Column(db.BigInteger, db.ForeignKey('events.event_id'))
	user_id = db.Column(db.BigInteger, db.ForeignKey('users.fb_id'))
	type = db.Column(db.BigInteger)
	
	def __init__(self, send_time, reminder_id, event_id, user_id, type):
		self.send_time = send_time
		self.reminder_id = reminder_id
		self.event_id = event_id
		self.user_id = user_id
		self.type = type
		
class Event(db.Model):
	__tablename__ = 'events'
	title = db.Column(db.String(200))
	description = db.Column(db.String(1500))
	uid = db.Column(db.BigInteger, db.ForeignKey('users.fb_id'))
	event_id  = db.Column(db.BigInteger, primary_key=True)
	start_time = db.Column(db.String(40))
	end_time = db.Column(db.String(40))
	location = db.Column(db.String(200))

	def __init__(self, title, description, uid, event_id, start_time, end_time, location):
		self.title = title
		self.description = description
		self.uid = uid
		self.event_id = event_id
		self.start_time = start_time
		self.end_time = end_time
		self.location = location
