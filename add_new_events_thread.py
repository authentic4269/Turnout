import util
from util import fb_call
import urllib2
import ast
import smtplib
from datetime import datetime, timedelta
import time
from os.path import abspath
from threading import Thread
import models
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def run():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    db = SQLAlchemy(app)
    app.config.from_object(__name__)
    events = get_all_users_new_events(db)
    for (user, new_events_list) in events:
        add_new_events_to_calendar(db, user, new_events_list)

def run2(db):
    events = get_all_users_new_events(db)
    for (user, new_events_list) in events:
        add_new_events_to_calendar(db, user, new_events_list)


def add_new_events_to_calendar(db, user, events):
    default_calendar_id = user.default_calendar
    google_service = util.get_google_serv(util.get_cred_storage(db, user.fb_id))
        
    for event in events:
	if not 'end_time' in event:
		event['end_time'] = event['start_time']	
        eventObj = {
            'summary': event['name'],
            'location': event['location'],
            'start': {
                'dateTime': event['start_time'],
                'timeZone': 'America/New_York'
             },
             'end': {
                'dateTime': event['end_time'],
                'timeZone': 'America/New_York'
              }
          }

        new_event = google_service.events().insert(calendarId=user.default_calendar, body=eventObj).execute()

          
def get_all_users_new_events(db):
    users = db.session.query(models.User).filter(models.User.auto_add == True)
    events = [] 
    for user in users:
            events.append((user, get_new_events_one_user(db, user)))
    return events
      
def get_new_events_one_user(db, user):
     access_token = db.session.query(models.User).get(user.fb_id).access_token
     access_token = access_token[1:len(access_token)-1]
     events = fb_call("me/events?limit=999&since=1990", args={'access_token': access_token})['data']
     ret = []
     for event in events:
        if (not db.session.query(models.Event).get(event['id'])) and is_in_future(event['start_time']):
                ret.append(event)
     return ret

def is_in_future(dt):
   d = datetime.strptime(dt[0:10], "%Y-%m-%d" )
   if (datetime.now() - d) < timedelta(seconds=1): 
        return True
   return False
    
