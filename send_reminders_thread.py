import util
from fabric.api import task
import smtplib
from datetime import datetime, timedelta
import time
import os
from os.path import abspath
from threading import Thread
import models

from flask import Flask
from flask_sqlalchemy import SQLAlchemy



@task
def run():
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
        db = SQLAlchemy(app)
        app.config.from_object(__name__)
	reminders = check_for_events(db)
	return send_all_reminders(db, reminders)

def run2(db, app):
	print "run2"
	reminders = check_for_events(db)
	return send_all_reminders(db, reminders)

def check_for_events(db):
        return(db.session.query(models.Reminder).filter(
		   (datetime.now() - models.Reminder.send_time) > timedelta (seconds = 1)))

def send_all_reminders(db, reminders):
	print "send_all"
	smtpobj = smtplib.SMTP("smtp.gmail.com", 587)
	smtpobj.ehlo()
	smtpobj.starttls()
	smtpobj.login("herokuturnoutapp@gmail.com", "cornelldelts")
	print "logged in"
	for reminder in reminders:
		send_one_reminder(db, reminder, smtpobj)
		db.session.delete(reminder)
	smtpobj.close()
	db.session.commit()

def send_one_reminder(db, reminder, smtpobj):
	event = db.session.query(models.Event).get(reminder.event_id)
	user = db.session.query(models.User).get(reminder.user_id)
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
		print to
		smtpobj.sendmail("herokuturnoutapp@gmail.com", to, msg)
	elif reminder.type == 1: #email
		header = 'To: ' + user.email + '\n' + 'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' + event.title	
		to = user.email
		msg = header + '\n This is a reminder for your event, ' + event.title + '\n\n'
	smtpobj.sendmail("herokuturnoutapp@gmail.com", to, msg)

