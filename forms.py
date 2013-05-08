from wtforms import Form, TextField, PasswordField, SelectField, IntegerField, BooleanField, validators
from models import User
import re

class GoogleForm(Form):
	default_action = SelectField(u'default_action', choices=[('always', 'Always'), ('never', 'Never')])
	calendar = SelectField(u'calendar', coerce=int)

class FacebookForm(Form):
	auto_remind = BooleanField(u'auto_remind')
	remind_time = IntegerField(u'reminder_time_count')
	remind_unit = SelectField(u'reminder_time_unit', choices=[('0', 'Minutes'), ('1', 'Hours'), ('2', 'Days')])
	auto_post = BooleanField(u'auto_post')
	post_time = IntegerField(u'post_time_count')
	post_unit = SelectField(u'post_time_unit', choices=[('0', 'Minutes'), ('1', 'Hours'), ('2', 'Days')])

class GlobalForm(Form):
	email = TextField('email', [validators.optional(), validators.Email()])
	phone = IntegerField('phone', [validators.optional()])
	carrier = SelectField('carrier', [validators.optional()], choices=[('att', '0'), ('sprint', '1'), ('verizon', '2'), ('tmobile', '3'), ('cricket', '4'), ('alltel', '5'), ])
	
	def validate_phone(form, field):
		if not re.match("^[0-9]{10}$", str(field.data)):
			raise validators.ValidationError("Expected a 10-digit phone number")
