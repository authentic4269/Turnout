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
from oauth2client.client import OAuth2WebServerFlow, Credentials
from oauth2client.tools import run
import models
from models import User, Reminder, Event

import requests
from flask import Flask, request, redirect, render_template, url_for, session, flash

class Storage():
    def put(param, arg):
        return

def get_google_cred():
    credentials = None

    if 'google_credentials' in session:
        credentials = Credentials.new_from_json(session['google_credentials'])

    if 'google_credentials' not in session or (credentials is None or credentials.invalid == True):
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

        credentials = run(FLOW, Storage())
        session['test'] = "hello"
        session['google_credentials'] = credentials.to_json()

    return credentials

def get_google(credentials):
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
