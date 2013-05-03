# -*- coding: utf-8 -*-

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

import requests
from flask import Flask, request, redirect, render_template, url_for

FB_APP_ID = os.environ.get('FACEBOOK_APP_ID')
requests = requests.session()

FLAGS = gflags.FLAGS
app_url = 'https://graph.facebook.com/{0}'.format(FB_APP_ID)
FB_APP_NAME = json.loads(requests.get(app_url).content).get('name')
FB_APP_SECRET = os.environ.get('FACEBOOK_SECRET')

def oauth_login_url(preserve_path=True, next_url=None):
    fb_login_uri = ("https://www.facebook.com/dialog/oauth"
                    "?client_id=%s&redirect_uri=%s" %
                    (app.config['FB_APP_ID'], get_home()))

    if app.config['FBAPI_SCOPE']:
        fb_login_uri += "&scope=%s" % ",".join(app.config['FBAPI_SCOPE'])
    return fb_login_uri


def simple_dict_serialisation(params):
    return "&".join(map(lambda k: "%s=%s" % (k, params[k]), params.keys()))


def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip('=')


def fbapi_get_string(path,
    domain=u'graph', params=None, access_token=None,
    encode_func=urllib.urlencode):
    """Make an API call"""

    if not params:
        params = {}
    params[u'method'] = u'GET'
    if access_token:
        params[u'access_token'] = access_token

    for k, v in params.iteritems():
        if hasattr(v, 'encode'):
            params[k] = v.encode('utf-8')

    url = u'https://' + domain + u'.facebook.com' + path
    params_encoded = encode_func(params)
    url = url + params_encoded
    result = requests.get(url).content

    return result


def fbapi_auth(code):
    params = {'client_id': app.config['FB_APP_ID'],
              'redirect_uri': get_home(),
              'client_secret': app.config['FB_APP_SECRET'],
              'code': code}

    result = fbapi_get_string(path=u"/oauth/access_token?", params=params,
                              encode_func=simple_dict_serialisation)
    pairs = result.split("&", 1)
    result_dict = {}
    for pair in pairs:
        (key, value) = pair.split("=")
        result_dict[key] = value

    return (result_dict["access_token"], result_dict["expires"])


def fbapi_get_application_access_token(id):
    token = fbapi_get_string(
        path=u"/oauth/access_token",
        params=dict(grant_type=u'client_credentials', client_id=id,
                    client_secret=app.config['FB_APP_SECRET']),
        domain=u'graph')

    token = token.split('=')[-1]
    if not str(id) in token:
        print 'Token mismatch: %s not in %s' % (id, token)
    return token


def fql(fql, token, args=None):
    if not args:
        args = {}

    args["query"], args["format"], args["access_token"] = fql, "json", token

    url = "https://api.facebook.com/method/fql.query"

    r = requests.get(url, params=args)
    return json.loads(r.content)


def fb_call(call, args=None):
    url = "https://graph.facebook.com/{0}".format(call)
    r = requests.get(url, params=args)
    return json.loads(r.content)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
app.config.from_object(__name__)
app.config.from_object('conf.Config')

def get_home():
    return 'https://' + request.host + '/'

def get_token():

    if request.args.get('code', None):
        return fbapi_auth(request.args.get('code'))[0]

    cookie_key = 'fbsr_{0}'.format(FB_APP_ID)

    if cookie_key in request.cookies:

        c = request.cookies.get(cookie_key)
        encoded_data = c.split('.', 2)

        sig = encoded_data[0]
        data = json.loads(urlsafe_b64decode(str(encoded_data[1]) +
            (64-len(encoded_data[1])%64)*"="))

        if not data['algorithm'].upper() == 'HMAC-SHA256':
            raise ValueError('unknown algorithm {0}'.format(data['algorithm']))

        h = hmac.new(FB_APP_SECRET, digestmod=hashlib.sha256)
        h.update(encoded_data[1])
        expected_sig = urlsafe_b64encode(h.digest()).replace('=', '')

        if sig != expected_sig:
            raise ValueError('bad signature')

        code =  data['code']

        params = {
            'client_id': FB_APP_ID,
            'client_secret': FB_APP_SECRET,
            'redirect_uri': '',
            'code': data['code']
        }

        from urlparse import parse_qs
        r = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        token = parse_qs(r.content).get('access_token')

        return token

def get_google(id):
    # Set up a Flow object to be used if we need to authenticate. This
    # sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
    # the information it needs to authenticate. Note that it is called
    # the Web Server Flow, but it can also handle the flow for native
    # applications
    # The client_id and client_secret are copied from the API Access tab on
    # the Google APIs Console
    FLOW = OAuth2WebServerFlow(
        client_id='499345994258-jkcmoa0r56sd6c2blsvbgccgjo5jpqel.apps.googleusercontent.com',
        client_secret='8SihSVq73-cJVAO3Qt58_KmI',
        scope='https://www.googleapis.com/auth/calendar',
        user_agent='Turnout/1')
    return "hello"

    # To disable the local server feature, uncomment the following line:
    # FLAGS.auth_local_webserver = False

    # If the Credentials don't exist or are invalid, run through the native client
    # flow. The Storage object will ensure that if successful the good
    # Credentials will get written back to a file.
    storage = Storage(id + '.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
      credentials = run(FLOW, storage)

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

@app.route('/google', methods=['GET'])
def google():
	return render_template('google.html')

@app.route('/facebook', methods=['GET'])
def facebook():
	return render_template('facebook.html')

@app.route('/global', methods=['GET'])
def global_opt():
	return render_template('global.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    # print get_home()

    access_token = get_token()
    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    if access_token:

        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})

        google_service = get_google(me['id'])

        url = request.url

        # creates user in database
        #from models import User
        #user = db.session.query(User).get(me['id'])
        #if not user:
            #newUser = User(me['name'], me['email'], me['id'])
            #db.session.add(newUser)
            #db.session.commit()
            #user = db.session.query(User).get(me['id'])

        # get events
        events = fb_call('me/events',
            args={'access_token': access_token})

        # get details for each event
        for event in events['data']:
            event['details'] = fb_call(str(event['id']),
                     args={'access_token': access_token})

        # get google calendars
        calendar_list = "hi"
        # calendar_list = google_service.calendarList().list().execute()

        return render_template(
            'index.html', app_id=FB_APP_ID, token=access_token, app=fb_app,
            me=me, name=FB_APP_NAME, events=events,
            calendar_list=calendar_list)
    #elif access_token:
	#return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name="access_token")
    #elif google_service:
	#return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name="google")
    else:
        return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME)

@app.route('/addToCalendar', methods=['GET', 'POST'])
def add_to_calendar():
    error = None
    if request.method == 'POST':

        google_service = get_google(request.form['id'])

        event = request.form['event']
        calendarId = request.form['calendar']

        import ast
        event = ast.literal_eval(event)

        eventObj = {
            'summary': event['name'],
            'location': event['location'],
            'start': {
                'dateTime': event['start_time'][:-5],
                'timeZone': event['timezone']
            },
            'end': {
                'dateTime': event['end_time'][:-5],
                'timeZone': event['timezone']
            }
        }

        new_event = google_service.events().insert(calendarId=calendarId, body=eventObj).execute()

        return new_event['id']

@app.route('/sendReminder', methods=['GET', 'POST'])
def send_reminder():
    import smtplib
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login('turnoutreminders@gmail.com', 'cs3300heroku')
    headers = ["from: turnoutreminders@gmail.com",
                "subject: " + request.form['eventname'],
                "to: " + request.form['email']]
    headers = "\r\n".join(headers)
    session.sendmail("turnoutreminders@gmail.com", request.form['email'], headers + "\r\n\r\n" + request.form['eventtime'] + "\n" + request.form['eventlocation'] + "\n\n" + request.form['eventdescr'])

    return render_template('channel.html')

@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')


@app.route('/close/', methods=['GET', 'POST'])
def close():
    return render_template('close.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if app.config.get('FB_APP_ID') and app.config.get('FB_APP_SECRET'):
        app.run(host='0.0.0.0', port=port)
    else:
        print 'Cannot start application without Facebook App Id and Secret set'
