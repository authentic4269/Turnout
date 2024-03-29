import urllib2

import base64
import os
import os.path
import urllib
import hmac
import json
import hashlib
from base64 import urlsafe_b64decode, urlsafe_b64encode
from flask_sqlalchemy import SQLAlchemy


import gflags
import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow, Credentials
from oauth2client.tools import run
import models
from models import User, Reminder, Event

import requests
from flask import Flask, request, redirect, render_template, url_for, session, flash

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications
# The client_id and client_secret are copied from the API Access tab on
# the Google APIs Console
FLOW = OAuth2WebServerFlow(
    client_id='499345994258-dckpi4k4dvm3660a2c94huf9tee3a9cj.apps.googleusercontent.com',
    client_secret='cFDEqr9pHqZs5-Xxdc3QpTv9',
    scope='https://www.googleapis.com/auth/calendar',
    redirect_uri='https://sheltered-basin-7772.herokuapp.com/oauth2callback',
    access_type='offline')

def fb_call(call, args=None):
    url = "https://graph.facebook.com/{0}".format(call)
    r = requests.get(url, params=args)
    return json.loads(r.content)

def fb_post(call, args=None):
    url = "https://graph.facebook.com/{0}".format(call)
    r = requests.post(url, params=args)
    return json.loads(r.content)

# returns true if credentials are valid
def ensure_cred(credentials):
    if credentials is None or credentials.invalid == True:
        return False

    return True

def get_google_code():
    credentials = None

    if 'google_cred' in session:
        credentials = Credentials.new_from_json(session['google_cred'])

    if credentials is None or credentials.invalid == True:
        return FLOW.step1_get_authorize_url()

def get_google_cred(db, userId, code):
    user = db.session.query(User).get(str(userId))
    print "potato"
    print str(user.google_cred)
    if len(str(user.google_cred)) > 5:
        #store in db
        http = httplib2.Http()
        credentials = Credentials.new_from_json(str(user.google_cred))
        credentials.refresh(http)

        user.google_cred = credentials.to_json()
        session['google_cred'] = user.google_cred
    else:
        credentials = FLOW.step2_exchange(code)
        session['google_cred'] = credentials.to_json()
        user.google_cred = credentials.to_json()
        db.session.commit()

    return credentials

def get_cred_storage(db, userId):
    #get from db
    user = db.session.query(User).get(str(userId))
    credentials = Credentials.new_from_json(str(user.google_cred))

    #refresh
    http = httplib2.Http()
    credentials.refresh(http)

    return credentials

def get_google_serv(credentials):
    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Build a service object for interacting with the API. Visit
    # the Google APIs Console
    # to get a developerKey for your own application.
    service = build(serviceName='calendar', version='v3', http=http,
           developerKey='AIzaSyAthlXADineWjQjLXtBiweEMbiUUONj7PI')
    return service
