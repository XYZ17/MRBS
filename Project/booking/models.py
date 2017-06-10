# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

import datetime
from django.db import models, connection
from django.conf import settings
from django.db.models.fields import Field
from django.utils.translation import gettext as _
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_model_changes import ChangesMixin,post_change
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render
from django.template import Context
from django.template.loader import render_to_string, get_template
import json
from django.http import JsonResponse,HttpResponse,HttpResponseBadRequest,HttpResponseNotFound
from ldapdb.models.fields import CharField, IntegerField, ListField
import ldapdb.models

class SerialField(Field):
	description = _("Integer")

	empty_strings_allowed = False
	default_error_messages = {
		'invalid': _("'%(value)s' value must be an integer."),
	}

	def __init__(self, *args, **kwargs):
		kwargs['blank'] = True
		super(SerialField, self).__init__(*args, **kwargs)

	def check(self, **kwargs):
		errors = super(SerialField, self).check(**kwargs)
		return errors

	def deconstruct(self):
		name, path, args, kwargs = super(SerialField, self).deconstruct()
		del kwargs['blank']
		return name, path, args, kwargs

	def get_internal_type(self):
		return "SerialField"

	def to_python(self, value):
		if value is None:
			return value
		try:
			return int(value)
		except (TypeError, ValueError):
			raise exceptions.ValidationError(
				self.error_messages['invalid'],
				code='invalid',
				params={'value': value},
			)

	def rel_db_type(self, connection):
		return IntegerField().db_type(connection=connection)

	def validate(self, value, model_instance):
		pass

	def get_db_prep_value(self, value, connection, prepared=False):
		if not prepared:
			value = self.get_prep_value(value)
			value = connection.ops.validate_autopk_value(value)
		return value

	def get_prep_value(self, value):
		value = super(SerialField, self).get_prep_value(value)
		if value is None:
			return None
		return int(value)

	def formfield(self, **kwargs):
		return None


class Booking(ChangesMixin, models.Model):
	booking_id = models.AutoField(db_column='Booking_ID', primary_key=True, verbose_name= 'Booking ID')  # Field name made lowercase.
	date = models.DateField(db_column='Date', verbose_name= 'Date')  # Field name made lowercase.
	starttime = models.TimeField(db_column='StartTime', verbose_name= 'Start Time')  # Field name made lowercase.
	endtime = models.TimeField(db_column='EndTime', verbose_name= 'End Time')  # Field name made lowercase.
	booking_title = models.CharField(db_column='Booking_Title', max_length=100, verbose_name= 'Title')  # Field name made lowercase.
	no_of_attendees = models.IntegerField(db_column='No_of_Attendees', blank=True, verbose_name= 'No. of attendees')  # Field name made lowercase.
	attendees = models.TextField(db_column='Attendees', blank=True, null=True, verbose_name= 'Attendees')  # Field name made lowercase. This field type is a guess.
	involve = models.CharField(db_column='Involve', max_length=30, blank=True, verbose_name= 'Involved')  # Field name made lowercase.
	equipment = models.TextField(db_column='Equipment', blank=True, null=True, verbose_name= 'Equipment(s)')  # Field name made lowercase. This field type is a guess.
	confidential = models.CharField(db_column='Confidential', max_length=10, default='No')  # Field name made lowercase.
	prioritize = models.CharField(db_column='Prioritize', max_length=10, default='No')  # Field name made lowercase.
	room = models.ForeignKey('Meetingroom', db_column='Room', verbose_name= 'Room')  # Field name made lowercase.
	booked_by = models.ForeignKey(settings.AUTH_USER_MODEL, to_field="username", db_column='Booked_By',verbose_name= 'Booked by')  # Field name made lowercase.
	booking_status = models.CharField(db_column='Booking_Status', max_length=10, default='Pending',verbose_name= 'Booking Status')  # Field name made lowercase.
	recursion_id = SerialField(db_column='Recursion_ID', unique=True, blank=True, null=True)  # Field name made lowercase.

	def __unicode__(self):
		return u'{0}'.format(self.equipment)

	class Meta:
		managed = True
		db_table = 'Booking'

@receiver(pre_save, sender=Booking)
def check_approval(sender, instance, **kwargs):
	if instance.previous_instance().booking_status == "Pending" and instance.booking_status == "Approve":
		with connection.cursor() as cursor:
			cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Date\" = %s AND \"StartTime\" <= %s::TIME AT TIME ZONE 'UTC' AND \"EndTime\" > %s::TIME AT TIME ZONE 'UTC' AND \"Room\"=%s AND \"Booking_Status\"='Approve'",(instance.date, instance.starttime, instance.starttime, instance.room.room_type))
			status1 = cursor.fetchone()
			status1 = status1[0]
			# print(status1)

			cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Date\" = %s AND \"StartTime\" < %s::TIME AT TIME ZONE 'UTC' AND \"EndTime\" > %s::TIME AT TIME ZONE 'UTC' AND \"Room\"=%s AND \"Booking_Status\"='Approve'",(instance.date, instance.endtime, instance.starttime, instance.room.room_type))
			status2 = cursor.fetchone()
			status2 = status2[0]
			# print(status2)

			cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Date\" = %s AND \"StartTime\" >= %s::TIME AT TIME ZONE 'UTC' AND \"EndTime\" <= %s::TIME AT TIME ZONE 'UTC' AND \"Room\"=%s AND \"Booking_Status\"='Approve'",(instance.date, instance.starttime, instance.endtime, instance.room.room_type))
			status3 = cursor.fetchone()
			status3 = status3[0]
			# print(status3)
					
			status = status1 + status2 + status3
			if status != 0:
				instance.booking_status = "Reject"
				messages.warning(request, "Booking clashing")
				# raise Exception("Booking clashing")
				# data = json.dumps({
				# 'status': 'error',
				# 'message': "Booking clashing"
				# })
				# return HttpResponseNotFound("Booking clashing")

	if instance.booking_status == "Approve" and instance.previous_instance().room.room_dscp != instance.room.room_dscp:
		with connection.cursor() as cursor:
			cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Date\" = %s AND \"StartTime\" <= %s::TIME AT TIME ZONE 'UTC' AND \"EndTime\" > %s::TIME AT TIME ZONE 'UTC' AND \"Room\"=%s AND \"Booking_Status\"='Approve'",(instance.date, instance.starttime, instance.starttime, instance.room.room_type))
			status1 = cursor.fetchone()
			status1 = status1[0]
			# print(status1)

			cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Date\" = %s AND \"StartTime\" < %s::TIME AT TIME ZONE 'UTC' AND \"EndTime\" > %s::TIME AT TIME ZONE 'UTC' AND \"Room\"=%s AND \"Booking_Status\"='Approve'",(instance.date, instance.endtime, instance.starttime, instance.room.room_type))
			status2 = cursor.fetchone()
			status2 = status2[0]
			# print(status2)

			cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Date\" = %s AND \"StartTime\" >= %s::TIME AT TIME ZONE 'UTC' AND \"EndTime\" <= %s::TIME AT TIME ZONE 'UTC' AND \"Room\"=%s AND \"Booking_Status\"='Approve'",(instance.date, instance.starttime, instance.endtime, instance.room.room_type))
			status3 = cursor.fetchone()
			status3 = status3[0]
			# print(status3)
					
			status = status1 + status2 + status3
			if status != 0:
				instance.room.room_dscp = instance.previous_instance().room.room_dscp
				raise Exception("Room Clashing")
			else:
				Id = instance.booking_id
				date = instance.date
				startTime = instance.starttime.strftime("%I:%M %p")
				endTime = instance.endtime.strftime("%I:%M %p")
				room_details = instance.room.room_dscp
				p_room_details = instance.previous_instance().room.room_dscp

				context={
					'ID' : Id,                                                                      
					'Date' : date,
					'StartTime' : startTime,
					'EndTime' : endTime,
					'PreviousRoom' : p_room_details + ' ('+ str(instance.previous_instance().room.room_type) + ')' ,
					'Room' : room_details + ' ('+ str(instance.room.room_type) + ')'
				}

				Reallocated_Message = get_template('mail/Reallocation.html').render(Context(context))
								
				Reallocated_Email = EmailMultiAlternatives("Meeting Room Booking Reallocated", Reallocated_Message, 'roombooking@hq.cdsb', [instance.booked_by.email])
				Reallocated_Email.attach_alternative(Reallocated_Message, "text/html")
				Reallocated_Email.send()
		

@receiver(post_save, sender=Booking)
def send_email_on_status_changed(sender, instance, **kwargs):

		if instance.previous_instance().booking_status == "Pending" and instance.booking_status == "Approve":

			Id = instance.booking_id
			date = instance.date
			startTime = instance.starttime.strftime("%I:%M %p")
			endTime = instance.endtime.strftime("%I:%M %p")
			title = instance.booking_title
			room_details = instance.room.room_dscp
			context={
				'ID' : Id,
				'Date' : date,
				'StartTime' : startTime,
				'EndTime' : endTime,
				'Title' : title,
				'Room' : room_details + ' ('+ str(instance.room.room_type) + ')'
			}
			Approve_Message = get_template('mail/Approve.html').render(Context(context))
							
			Approve_Email = EmailMultiAlternatives("Meeting Room Booking Confirmation", Approve_Message, 'roombooking@hq.cdsb', [instance.booked_by.email])
			Approve_Email.attach_alternative(Approve_Message, "text/html")
			Approve_Email.send()
		

		elif instance.previous_instance().booking_status == "Pending" and instance.booking_status == "Reject" or instance.previous_instance().booking_status == "Approve" and instance.booking_status == "Reject":
			Id = instance.booking_id
			date = instance.date
			startTime = instance.starttime.strftime("%I:%M %p")
			endTime = instance.endtime.strftime("%I:%M %p")
			title = instance.booking_title
			room_details = instance.room.room_dscp
			context={
				'ID' : Id,
				'Date' : date,
				'StartTime' : startTime,
				'EndTime' : endTime,
				'Title' : title,
				'Room' : room_details + ' ('+ str(instance.room.room_type) + ')'
			}
			Reject_Message = get_template('mail/Reject.html').render(Context(context))
							
			Reject_Email = EmailMultiAlternatives("Meeting Room Booking Rejected", Reject_Message, 'roombooking@hq.cdsb', [instance.booked_by.email])
			Reject_Email.attach_alternative(Reject_Message, "text/html")
			Reject_Email.send()

class Meetingroom(models.Model):
	room_type = models.CharField(db_column='Room_Type', primary_key=True, max_length=10, verbose_name= 'Size' )  # Field name made lowercase.
	room_dscp = models.TextField(db_column='Room_Dscp', blank=True, null=True, verbose_name= 'Description')  # Field name made lowercase.
	room_noofperson = models.CharField(db_column='Room_NoOfPerson', max_length=50, blank=True, null=True, verbose_name= 'Recommended No. of Person')  # Field name made lowercase.

	def __str__(self):
		return str(self.room_type)

	class Meta:
		managed = True
		db_table = 'MeetingRoom'


class User(models.Model):
	user_id = models.CharField(db_column='User_ID', primary_key=True, max_length=50)  # Field name made lowercase.
	user_name = models.CharField(db_column='User_Name', max_length=50)  # Field name made lowercase.
	user_email = models.CharField(db_column='User_Email', max_length=320)  # Field name made lowercase.
	user_password = models.CharField(db_column='User_Password', max_length=100)  # Field name made lowercase.
	user_post = models.CharField(db_column='User_Post', max_length=100, blank=True, null=True)  # Field name made lowercase.
	user_office = models.SmallIntegerField(db_column='User_Office')  # Field name made lowercase.
	user_isactive = models.BooleanField(db_column='User_isActive')  # Field name made lowercase.
	user_isadmin = models.BooleanField(db_column='User_isAdmin')  # Field name made lowercase.

	class Meta:
		managed = True
		db_table = 'User'

class AuthUser(models.Model):
	password = models.CharField(max_length=128)
	last_login = models.DateTimeField(blank=True, null=True)
	is_superuser = models.BooleanField(editable=True)
	username = models.CharField(unique=True, max_length=150)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	email = models.CharField(max_length=254)
	is_staff = models.BooleanField()
	is_active = models.BooleanField(editable=True)
	date_joined = models.DateTimeField()

	def __str__(self):
		return self.first_name

	def __unicode__(self):
		return self.first_name

	class Meta:
		managed = True
		db_table = 'auth_user'
"""
#LDAP USER DB
class AuthUser(ldapdb.models.Model):

	# LDAP meta-data
	base_dn = "ou=personal,dc=global-addressbook,dc=com"
	object_classes = ['posixGroup']

	password = models.CharField(db_column='userPassword',max_length=128)
	last_login = models.DateTimeField(blank=True, null=True)
	is_superuser = models.BooleanField(editable=True)
	username = models.CharField(db_column='uid',unique=True, max_length=150)
	first_name = models.CharField(db_column='cn',max_length=30)
	last_name = models.CharField(db_column='sn',max_length=30)
	email = models.CharField(db_column='mail',max_length=254)
	is_staff = models.BooleanField()
	is_active = models.BooleanField(editable=True)
	date_joined = models.DateTimeField()

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	class Meta:
		managed = True
		db_table = 'auth_user'
"""