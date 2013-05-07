import urllib2

def get_refresh_token(id):
	return(urllib2.urlopen("https://accounts.google.com/o/oauth2/auth?client_id=803369941061.apps.googleusercontent.com&response_type=code&scope=https://www.googleapis.com/auth/calendar&access_type=offline&redirect_uri=http://sheltered-basin-7772.herokuapp.com/google_auth&state=" + str(id)))
