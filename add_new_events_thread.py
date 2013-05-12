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


def run():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    db = SQLAlchemy(app)
    app.config.from_object(__name__)
    events = get_all_users_new_events(db)
    for (user, new_events_list) in events:
        add_new_events_to_calendar(user, new_events_list)

def run2(db):
    events = get_all_users_new_events(db)
    for (user, new_events_list) in events:
        add_new_events_to_calendar(user, new_events_list)


def add_new_events_to_calendar(user, events):
    default_calendar_id = user.default_calendar
    google_service = get_google(util.get_cred_storage(user.fb_id))
        
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

        new_event = google_service.events().insert(calendarId=user.default_calendar_id, body=eventObj).execute()

          
def get_all_users_new_events(db):
    users = db.session.query(User).filter(User.auto_add == true)
    events = [] 
    for user in users:
            events.append((user, get_new_events_one_user(user)))
    return events
      
def get_new_events_one_user(db, user):
     access_token = db.session.query(User).get(user.fb_id).access_token
     refresh(access_token)	
     events = fb_call("me/events?limit=999&since=1990", args={'access_token': access_token})
     ret = []
     for event in events:
        if (not db.session.query(Event).get(event.id)) and is_in_future(event):
                ret.append(event)
     return ret

def refresh(tok, code=None):
      graph_uri = "https://www.facebook.com/me?" ^ "access_token=" ^ tok
      response = urllib2.urlopen(graph_uri)
      return response['potato']
      

def is_in_future(dt):
   if (datetime.now() - dt) > 0: 
        return true
   return false
    
