# -*- coding: utf-8 -*-
import urllib2
import util
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
import models, forms
from models import User, Reminder, Event
from forms import GoogleForm, FacebookForm, GlobalForm

import requests
from flask import Flask, request, redirect, render_template, url_for, session, flash

FB_APP_ID = os.environ.get('FACEBOOK_APP_ID')
requests = requests.session()

FLAGS = gflags.FLAGS
def process_flags(argv):
    try:
        argv = FLAGS(argv)  # parse flags
    except gflags.FlagsError, e:
        print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
        sys.exit(1)


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
app.config['SESSION_COOKIE_DOMAIN'] = 'sheltered-basin-7772.herokuapp.com'
db = SQLAlchemy(app)
app.config.from_object(__name__)
app.config.from_object('conf.Config')
app.secret_key = os.urandom(22)

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

@app.route('/google_auth', methods=['GET', 'POST'])
def get_google_auth(token):
    response = urllib2.urlopen("https://accounts.google.com/o/oauth2/token&refresh_token=" + token + "&client_id=499345994258-dckpi4k4dvm3660a2c94huf9tee3a9cj.apps.googleusercontent.com&client_secret=cFDEqr9pHqZs5-Xxdc3QpTv9&grant_type=refresh_token")
    return response.access_token

@app.route('/google', methods=['GET', 'POST'])
def googlesettings():
    if request.method == 'POST' and 'user' in session:
        f = GoogleForm(request.form)
        session['user'].update({'default_calendar': f.calendar.data, 'auto_add': session['user'].auto_add})
    elif 'user' in session and 'google_service' in session:
        return render_template('google.html', calendars_list=google_service.calendarList().list().execute(), 
        default_calendar=session['user'].default_calendar, auto_add=session['user'].auto_add)
    else:
        flash('You are not logged in')
        return redirect(url_for('index'))
    

@app.route('/facebook', methods=['GET', 'POST'])
def facebooksettings():
    return render_template('sessions.html', text=session)
    if request.method == 'POST' and 'user' in session:
        f = FacebookForm(request.form)

        user = db.session.query(User).get(session['user'].fb_id)
        user.remind_by_default = f.auto_remind.data
        user.post_by_default = f.auto_post.data
        user.reminder_time = convert(f.reminder_time_count.data, f.reminder_time_unit.data)
        user.post_time = convert(f.post_time_count.data, f.post_time_unit.data)
        db.session.commit()

        session['user'] = user
   
        flash('Facebook Settings Updated!')
        return redirect(url_for('index'))
    elif 'user' in session:
        remind_inf = get_unit(session['user'].reminder_time)
        post_inf = get_unit(session['user'].post_time)
        return render_template('facebook.html', auto_remind=session['user'].remind_by_default,
            remind_time=remind_inf['num'], remind_unit=remind_inf['unit'], 
            post_time=post_inf['num'], post_unit=post_inf['unit'])
    else:
        flash('You are not logged in')
        return redirect(url_for('index'))

def convert(num, unit):
    num = int(num)
    unit = int(unit)

    if unit == 0:
        return num
    elif unit == 1:
        return num * 60
    elif unit == 2: 
        return num * 60 * 24

def get_unit(num):
    if (num % (60 * 24)) == 0:
        return({'num': (num / (60 * 24)), 'unit': 2})
    elif (num % 60) == 0:
        return({'num': (num / 60), 'unit': 1})
    else:
        return({'num': num, 'unit': 0})

@app.route('/global', methods=['GET', 'POST'])
def global_opt():
    if request.method == 'POST' and 'user' in session:
        f = GlobalForm(request.form)
        if (f.validate()):
            user = db.session.query(User).get(session['user'].fb_id)
            user.email = f.email.data
            user.phone = f.phone.data
            user.carrier = f.carrier.data
            db.session.commit()

            session['user'] = user
            flash('Settings updated')
            return redirect(url_for('index'))
        else:
            return render_template('global.html', form=f, email=session['user'].email, phone=session['user'].phone, carrier=session['user'].carrier)
    elif 'user' in session:
        return render_template('global.html', form="", email=session['user'].email, phone=session['user'].phone, carrier=session['user'].carrier)
    else:
        flash('You are not logged in')
        return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if not 'facebook' in session:
        access_token = get_token()
        if access_token is not None:
            session['facebook'] = access_token
    else:
        access_token = session['facebook']

    channel_url = url_for('get_channel', _external=True)
    channel_url = channel_url.replace('http:', '').replace('https:', '')

    if access_token:
        me = fb_call('me', args={'access_token': access_token})
        fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})

        url = request.url

        # creates user in database
        user = db.session.query(User).get(me['id'])
        if not user:
            newUser = User(me['name'], me['email'], me['id'])
            db.session.add(newUser)
            db.session.commit()
            user = db.session.query(User).get(me['id'])

        google_cred = util.get_google_cred()
        #google_service = util.get_google(google_cred)
        #session['google_service'] = google_service
        session['user'] = user

        # get events
        events = fb_call('me/events',
            args={'access_token': access_token})
        # get details for each event
        for event in events['data']:
            event['details'] = fb_call(str(event['id']),
                     args={'access_token': access_token})

        calendar_list = "hi"
        #calendar_list = google_service.calendarList().list().execute()

        return render_template(
            'index.html', app_id=FB_APP_ID, token=access_token, app=fb_app,
            me=me, name=FB_APP_NAME, events=events,
            calendar_list=calendar_list, session=session)
    else:
        return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME)

@app.route('/addToCalendar', methods=['GET', 'POST'])
def add_to_calendar():
    error = None
    if request.method == 'POST':
        user.update({"auto_add": form.default_action.data, "default_calendar": form.calendar.data})
        google_service = util.get_google(request.form['id'])
    
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

@app.route('/googleme', methods=['GET', 'POST'])
def get_googleme():
    credentials = util.get_google_cred()
    google_service = util.get_google(credentials)
    text = google_service.calendarList().list().execute()
    return render_template('sessions.html', text=text)

@app.route('/close/', methods=['GET', 'POST'])
def close():
    return render_template('close.html')

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 80))
    if app.config.get('FB_APP_ID') and app.config.get('FB_APP_SECRET'):
        app.run(host='0.0.0.0', port=port)
    else:
        print 'Cannot start application without Facebook App Id and Secret set'
