import utils
import smtplib
from datetime import datetime, timedelta
import time
from os.path import abspath
from threading import Thread
import models
ifrom flask import Flask
from flask_sqlalchemy import SQLAlchemy


class ReminderThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
        db = SQLAlchemy(app)
        app.config.from_object(__name__)

    def run(self):
        events = self.check_for_new_events()
        return send_all_reminders(reminders)

    def check_for_new_events(self):
	users = db.session.query(User).filter(User.auto_add = true)
	events = []
	for user in users:
		events.append(get_new_events_user(user))
	return events

    def get_new_events(self, user):
	access_token = db.session.query(User).get(User.fb_id=user.fb_id)['access_token']
	events = fb_call("me/events?limit=999&until=now&since=1990", args={'access_token': access_token})
	for event in events
		if db.session
