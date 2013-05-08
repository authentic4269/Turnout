import util
import ast
import smtplib
from datetime import datetime, timedelta
import time
from os.path import abspath
from threading import Thread
import models
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

class ReminderThread(Thread):

	def __init__(self):
	        Thread.__init__(self)
	        app = Flask(__name__)
	        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
		db = SQLAlchemy(app)
		app.config.from_object(__name__)

	def run(self):
        	events = get_all_users_new_events()
		for (user, new_events_list) in events:
			add_new_events_to_calendar(user, new_events_list)


	def add_new_events_to_calendar(user, events):
	    	default_calendar_id = user.default_calendar
	        google_service = get_google(user.id)
		for e in events:
	        	event = ast.literal_eval(e)

	        	eventObj = {
	        	    'summary': event.name,
	        	    'location': event.location,
	        	    'start': {
	        	        'dateTime': event.start_time,
	        	        'timeZone': event.timezone
	        	    },
	        	    'end': {
	        	        'dateTime': event.end_time,
	        	        'timeZone': event.timezone
	        	    }
	        	}

	        	new_event = google_service.events().insert(calendarId=default_calendar_id, body=eventObj).execute()
	
          
	def get_all_users_new_events(self):
	        users = db.session.query(User).filter(User.auto_add == true)
	        events = [] 
	        for user in users:
	                events.append((user, get_new_events_one_user(user)))
	        return events
      
	def get_new_events_one_user(self, user):
        	access_token = db.session.query(User).get(User.fb_id == user.fb_id)['access_token']
        	events = fb_call("me/events?limit=999&until=now&since=1990", args={'access_token': access_token})
        	ret = []
        	for event in events:
        	        if not db.session.query(Event).get(event.id) and is_in_future(event):
        	                ret.append(event)
        	return ret


