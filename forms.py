from flask.wtf import Form, TextField, PasswordField, validators
from models import User

class GoogleForm(Form):
	action = SelectField(u'default_action', choices=[('always', 'Always'), ('ask', 'Ask Me'), ('never', 'Never')])
	calendar = SelectField(u'calendar', coerce=int)
	
	def edit_google_settings(request, fb_id):
		user = User.query.get(fb_id)
		form = GoogleForm(request.POST, obj=user)		
		form.calendar.choices = [(1, "Facebook"), (2, "Work")]

class FacebookForm(Form):
	auto_remind = BooleanField(u'auto_remind')
	deliver_reminders = IntegerField(u'reminder_time_count')
	deliver_time_unit = SelectField(u'reminder_time_unit', choices=[('m', 'Minutes'), ('h', 'Hours'), ('d', 'Days')])
	auto_post = BooleanField(u'auto_post')
	post_reminders = IntegerField(u'post_time_count')
	post_time_unit = SelectField(u'post_time_unit', choices=[('p_m', 'Minutes'), ('p_h', 'Hours'), ('p_d', 'Days')])

class GlobalForm(Form):
	email = TextField(u'email')
	phone = IntegerField(u'phone')
	carrier = SelectField(u'carrier', choices=[('att', 'AT&T'), ('sprint', 'Sprint'), ('verizon', 'Verizon'), ('tmobil', 'TMobile'), ('cricket', 'Cricket')])
	
