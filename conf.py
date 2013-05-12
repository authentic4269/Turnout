import os

class Config(object):
    DEBUG = True
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    GOOGLE_CLIENT_SECRET = "cFDEqr9pHqZs5-Xxdc3QpTv9"
    GOOGLE_CLIENT_ID = "499345994258-dckpi4k4dvm3660a2c94huf9tee3a9cj.apps.googleusercontent.com"
    GOOGLE_API_KEY = "AIzaSyAthlXADineWjQjLXtBiweEMbiUUONj7PI"
    FBAPI_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FBAPI_APP_SECRET = os.environ.get('FACEBOOK_SECRET')
    FBAPI_SCOPE = ['user_events', 'user_likes', 'user_photos', 'user_photo_video_tags']
