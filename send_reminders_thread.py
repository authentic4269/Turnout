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
        self.check_for_events()

    def check_for_events(self):
        reminders = db.session.query(Reminder).filter(
		    (datetime.now() - Reminder.send_time) > timedelta (seconds = 1))
	send_all_reminders(reminders)

    def send_all_reminders(self, reminders):
		smtpobj = smtplib.SMTP(smtp.gmail.com, 465)
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
			header = 'To: ' + str(user.phone) + '@txt.att.net' + '\n' +
			'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' +
			event.title
			to = str(user.phone) + '@txt.att.net'
		else if user.carrier == 1: #sprint
                        header = 'To: ' + str(user.phone) + '@messaging.sprintpcs.com' + '\n' +
                        'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' +
                        event.title
			to = str(user.phone) + '@messaging.sprintpcs.com'
		else if user.carrier == 2: #verizon
                        header = 'To: ' + str(user.phone) + '@vtext.com' + '\n' +
                        'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' +
                        event.title
			to = str(user.phone) + '@vtext.com'
		else if user.carrier == 3: #tmobile
                        header = 'To: ' + str(user.phone) + '@tmomail.net' + '\n' +
                        'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' +
                        event.title
			to = str(user.phone) + '@tmomail.net'
		else if user.carrier == 4: #cricket
                        header = 'To: ' + str(user.phone) + '@sms.mycricket.com' + '\n' +
                        'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' +
                        event.title
			to = str(user.phone) + '@sms.mycricket.com'
		else if user.carrier == 5: #alltel
                        header = 'To: ' + str(user.phone) + '@sms.alltelwireless.com' + '\n' +
                        'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 'Subject: ' +
                        event.title
			to = str(user.phone) + '@sms.alltelwireless.com'
		msg = header + '\n This is a reminder for your event, ' + event.title + '\n\n'
		smtpobj.sendmail(herokuturnoutapp@gmail.com, to, msg)
	else if reminder.type == 1: #email
		header = 'To: ' + user.email + '\n' + 'From: ' + 'herokuturnoutapp@gmail.com' + '\n' + 
		'Subject: ' + event.title	
		msg = header + '\n This is a reminder for your event, ' + event.title + '\n\n'
		smtpobj.sendmail(herokuturnoutapp@gmail.com, to, msg)

