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
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
import models
from models import User, Reminder, Event

import requests
from flask import Flask, request, redirect, render_template, url_for, session, flash

def get_google(id):
    # Set up a Flow object to be used if we need to authenticate. This
    # sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
    # the information it needs to authenticate. Note that it is called
    # the Web Server Flow, but it can also handle the flow for native
    # applications
    # The client_id and client_secret are copied from the API Access tab on
    # the Google APIs Console
    FLOW = OAuth2WebServerFlow(
        redirect_uri='urn:ietf:wg:oauth:2.0:oob',
        client_id='499345994258-dckpi4k4dvm3660a2c94huf9tee3a9cj.apps.googleusercontent.com',
        client_secret='cFDEqr9pHqZs5-Xxdc3QpTv9',
        scope='https://www.googleapis.com/auth/calendar',
        access_type='offline')
   
    # To disable the local server feature, uncomment the following line:
    # FLAGS.auth_local_webserver = False

    # If the Credentials don't exist or are invalid, run through the native client
    # flow. The Storage object will ensure that if successful the good
    # Credentials will get written back to a file.
    storage = Storage('calendars/' + id + '.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
      credentials = run(FLOW, storage)
    #refresh_token = credentials.to_json().refresh_token
    #db.session.query(User).filter(fb_id=id).update({'refresh_token': refresh_token})
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
