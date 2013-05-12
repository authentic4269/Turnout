import util
import smtplib
from datetime import datetime, timedelta
import time
from os.path import abspath
from threading import Thread
import models
from flask import Flask
from flask_sqlalchemy import SQLAlchemy



def __init__(self):
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
	db = SQLAlchemy(app)
	app.config.from_object(__name__)

def run(self):
	reminders = self.check_for_events()
	return send_all_reminders(reminders)

def check_for_events(self):
	return db.session.query(Reminder)
#        return(db.session.query(Reminder).filter(
#		    (datetime.now() - Reminder.send_time) > timedelta (seconds = 1)))

def send_all_reminders(self, reminders):
	smtpobj = smtplib.SMTP("smtp.gmail.com", 465)
	smtpobj.ehlo()
	smtpobj.starttls()
	smtpobj.login(herokuturnoutapp, cornelldelts)
	for reminder in reminders:
		send_one_reminder(self, reminder, smtpobj)
		db.session.delete(reminder)
	smtpobj.close()

def send_one_reminder(self, reminder, smtpobj):
	event = self.db.session.query(Event).get(event_id=reminder.event_id)
	user = self.db.session.query(User).get(fb_id=reminder.user_id)
	if reminder.type == 0: #text message:
		if user.carrier == 0: #att
			header = 'To: ' + str(user.phone) + '@txt.att.net' + '\n' + 'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' + event.title
			to = str(user.phone) + '@txt.att.net'
		elif user.carrier == 1: #sprint
			header = 'To: ' + str(user.phone) + '@messaging.sprintpcs.com' + '\n' + 'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' + event.title
			to = str(user.phone) + '@messaging.sprintpcs.com'
		elif user.carrier == 2: #verizon
			header = 'To: ' + str(user.phone) + '@vtext.com' + '\n' + 'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' + event.title
			to = str(user.phone) + '@vtext.com'
		elif user.carrier == 3: #tmobile
			header = 'To: ' + str(user.phone) + '@tmomail.net' + '\n' + 'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' + event.title
			to = str(user.phone) + '@tmomail.net'
		elif user.carrier == 4: #cricket
			header = 'To: ' + str(user.phone) + '@sms.mycricket.com' + '\n' + 'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' + event.title
			to = str(user.phone) + '@sms.mycricket.com'
		elif user.carrier == 5: #alltel
			header = 'To: ' + str(user.phone) + '@sms.alltelwireless.com' + '\n' + 'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' + event.title
			to = str(user.phone) + '@sms.alltelwireless.com'
		msg = header + '\n This is a reminder for your event, ' + event.title + '\n\n'
		smtpobj.sendmail("herokuturnoutapp@gmail.com", to, msg)
	elif reminder.type == 1: #email
		header = 'To: ' + user.email + '\n' + 'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' + event.title	
		msg = header + '\n This is a reminder for your event, ' + event.title + '\n\n'
	smtpobj.sendmail("herokuturnoutapp@gmail.com", to, msg)

