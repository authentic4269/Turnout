from wtforms import Form, TextField, PasswordField, SelectField, IntegerField, BooleanField, validators
from models import User
import re

class GoogleForm(Form):
	auto_add = SelectField(u'auto_add', choices=[('always', 'Always'), ('never', 'Never')])
	calendar = SelectField(u'calendar', [validators.Email()])

class FacebookForm(Form):
	auto_remind = BooleanField('auto_remind')
	reminder_time_count = IntegerField('reminder_time_count')
	reminder_time_unit = SelectField('reminder_time_unit', choices=[('0', 'Minutes'), ('1', 'Hours'), ('2', 'Days')])
	auto_post = BooleanField('auto_post')
	post_time_count = IntegerField('post_time_count')
	post_time_unit = SelectField('post_time_unit', choices=[('0', 'Minutes'), ('1', 'Hours'), ('2', 'Days')])

class GlobalForm(Form):
	email = TextField('email', [validators.optional(), validators.Email()])
	phone = IntegerField('phone', [validators.optional()])
	carrier = SelectField('carrier', [validators.optional()], choices=[('0', 'AT&T'), ('1', 'Sprint'), ('2', 'Verizon'), ('3', 'TMobile'), ('4', 'Cricket'), ('5', 'Alltel'), ])
	
	def validate_phone(form, field):
		if not re.match("^[0-9]{10}$", str(field.data)):
			raise validators.ValidationError("Expected a 10-digit phone number")
