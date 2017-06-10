from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import serializers
from django.core.mail import send_mass_mail, BadHeaderError, EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime
from django.views.decorators.cache import cache_control,never_cache

import datetime
import json

import forms as f
from booking import models as m
from django.db import connection

#LDAP
from django_auth_ldap.backend import LDAPBackend
LDAP = LDAPBackend()

##Tables
from datatableview import Datatable, ValuesDatatable, columns
from datatableview.views import DatatableView, MultipleDatatableView, XEditableDatatableView
from datatableview.views.legacy import LegacyDatatableView
from datatableview import helpers
from django_tables2 import RequestConfig
from .tables import RoomTable

#Autocomplete
from dal import autocomplete

decorators = [never_cache, login_required]
admin_decorators = [never_cache, login_required, user_passes_test(lambda u: u.is_superuser)]

def get_pending_request(request):
	with connection.cursor() as cursor:
		cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Booking_Status\" = \'Pending\' AND (\"Date\" + \"StartTime\") >= (date %s + time %s)",(datetime.datetime.now().date(), datetime.datetime.now().time() ))
		pending_request = cursor.fetchone()
		return pending_request[0]

class AutocompleteUser(autocomplete.Select2QuerySetView):
	def get_queryset(self):
		qs = m.AuthUser.objects.all()
		qs = qs.filter(first_name__icontains=self.q)

		return qs


@never_cache
@login_required(login_url="/login/")
def new_booking(request): 
	form = f.BookingForm()
	table = RoomTable(m.Meetingroom.objects.all().order_by('-room_type'))
	RequestConfig(request, paginate=False).configure(table)
	context = Context({
	'form': form,
	'table': table,
	'pending_request': get_pending_request(request)
	})
	if request.method == 'POST':
			date = request.POST.get('date')
			startTime = request.POST.get('startTime')
			endTime = request.POST.get('endTime')
			booking_title = request.POST.get('title')
			user = request.POST.get('user')
			booked_by = request.user
			room_size = request.POST.get('RoomRadio')
			room = m.Meetingroom.objects.get(room_type=room_size)
			no_of_attendees = request.POST.get('NoAttendees')
			attendees = request.POST.get('attendees')
			involve = request.POST.get('InvolvesRadio')
			equipment = request.POST.getlist('EquipCheckboxes[]')
			equipment = str(map(str, equipment)).replace('[', '').replace(']', '').replace("'", '')
			# equipment = equipment.replace('[', '{').replace(']', '}')
			# equipment = np.array(equip)
			confidential = request.POST.get('confidential')
			booking_type = request.POST.get('booking_type')
			r_no = request.POST.get('r_no')
			r_length = request.POST.get('r_length')
			recursion_id = None

			with connection.cursor() as cursor:
				cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Date\" = %s AND \"StartTime\" <= %s::TIME AT TIME ZONE 'UTC' AND \"EndTime\" > %s::TIME AT TIME ZONE 'UTC' AND \"Room\"=%s AND \"Booking_Status\"='Approve'",(date, startTime, startTime, room_size))
				status1 = cursor.fetchone()
				status1 = status1[0]
				# print(status1)

				cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Date\" = %s AND \"StartTime\" < %s::TIME AT TIME ZONE 'UTC' AND \"EndTime\" > %s::TIME AT TIME ZONE 'UTC' AND \"Room\"=%s AND \"Booking_Status\"='Approve'",(date, endTime, startTime, room_size))
				status2 = cursor.fetchone()
				status2 = status2[0]
				# print(status2)

				cursor.execute("SELECT COUNT(*) FROM \"Booking\" WHERE \"Date\" = %s AND \"StartTime\" >= %s::TIME AT TIME ZONE 'UTC' AND \"EndTime\" <= %s::TIME AT TIME ZONE 'UTC' AND \"Room\"=%s AND \"Booking_Status\"='Approve'",(date, startTime, endTime, room_size))
				status3 = cursor.fetchone()
				status3 = status3[0]
				# print(status3)

				cursor.execute("SELECT email FROM auth_user WHERE is_superuser = 'True'")
				admin_list = [row[0].encode('ascii') for row in cursor.fetchall()]
				
			status = status1 + status2 + status3
			recurring = {}
			dateList = []

			if booking_type == "Normal" :
				if status == 0 :
					booking = m.Booking(
						date = date,
						starttime = startTime,
						endtime = endTime,
						booking_title = booking_title,
						booked_by = booked_by,
						no_of_attendees = no_of_attendees,
						# attendees = attendees,
						involve = involve,
						equipment = equipment,
						confidential = confidential,
						room = room,
						recursion_id = recursion_id,
						)
					booking.save()

					Id = booking.pk
					startTime = datetime.datetime.strptime(startTime,"%H:%M")
					endTime = datetime.datetime.strptime(endTime,"%H:%M")
					startTime = startTime.strftime("%I:%M %p")
					endTime = endTime.strftime("%I:%M %p")
					date = date
					title = booking_title
					room_details = m.Meetingroom.objects.values_list('room_dscp').get(room_type = room)
					room_details = str(room_details).replace("(u'", '').replace("',)", '')

					context={
						'ID' : Id,
						'User' : request.user.first_name,
						'Date' : date,
						'StartTime' : startTime,
						'EndTime' : endTime,
						'Title' : title,
						'Room' : room_details + ' ('+ str(room) + ')'
					}

					User_Message = get_template('mail/User.html').render(Context(context))
					Admin_Message = get_template('mail/Admin.html').render(Context(context))
							
					User_Email = EmailMultiAlternatives("Meeting Room Booking", User_Message, 'roombooking@hq.cdsb', [request.user.email])
					User_Email.attach_alternative(User_Message, "text/html")
					User_Email.send()

					Admin_Email = EmailMultiAlternatives('New Meeting Room Booking Request', Admin_Message , 'roombooking@hq.cdsb', admin_list)
					Admin_Email.attach_alternative(Admin_Message, "text/html")
					Admin_Email.send()

				else:
					return HttpResponse("The meeting room is not available.", status=400)
					#messages.error(request, "Date/Time for Room chosen is not available. Please select again.")

			elif booking_type == "Recurring" :
				if status == 0 :
					recurring['date'] = date
					with open('recurring', 'a') as outfile:
						json.dump(recurring, outfile)

					if r_no == r_length :
						with open('recurring') as r:
							for obj in iterparse(r):
								booking = m.Booking(
									date = obj[u'date'],
									starttime = startTime,
									endtime = endTime,
									booking_title = booking_title,
									booked_by = booked_by,
									no_of_attendees = no_of_attendees,
									# attendees = attendees,
									involve = involve,
									equipment = equipment,
									confidential = confidential,
									room = room,
									recursion_id = recursion_id,
									)
								booking.save()
								dateList.append(obj[u'date'])
					
							##RECURRING EMAIL NOTIFICATION##

							startDate = dateList[0]
							endDate = dateList[-1]
							startTime = datetime.datetime.strptime(startTime,"%H:%M")
							endTime = datetime.datetime.strptime(endTime,"%H:%M")
							startTime = startTime.strftime("%I:%M %p")
							endTime = endTime.strftime("%I:%M %p")
							title = booking_title
							room_details = m.Meetingroom.objects.values_list('room_dscp').get(room_type = room)
							room_details = str(room_details).replace("(u'", '').replace("',)", '')

							context={
								'User' : request.user.first_name,
								'Date' : startDate + ' till ' + endDate,
								'StartTime' : startTime,
								'EndTime' : endTime,
								'Title' : title,
								'Room' : room_details + ' ('+ str(room) + ')'
							}

							User_Message = get_template('mail/User.html').render(Context(context))
							Admin_Message = get_template('mail/Admin.html').render(Context(context))
							
							User_Email = EmailMultiAlternatives("Meeting Room Booking", User_Message, 'roombooking@hq.cdsb', [request.user.email])
							User_Email.attach_alternative(User_Message, "text/html")
							User_Email.send()

							Admin_Email = EmailMultiAlternatives('New Meeting Room Booking Request', Admin_Message , 'roombooking@hq.cdsb', admin_list)
							Admin_Email.attach_alternative(Admin_Message, "text/html")
							Admin_Email.send()
						
						with open('recurring', 'w'):
							pass

				else:
					with open('recurring', 'w'):
						pass
					return HttpResponse("The meeting room is not available.", status=400)
					#messages.error(request, "Date/Time for Room chosen is not available. Please select again.")	
			
			return HttpResponseRedirect('booking/MyBooking.html')
	else:
		return render(request, 'booking/NewBooking.html', context)

def verify_booking(booking_data, status):

	bsdt = booking_data['startDateTime']
	bedt = booking_data['endDateTime']
	room = booking_data['room']
	#booking_data['involve'] = involve

# Pass form data to model
def iterparse(file_obj):
	decoder = json.JSONDecoder()
	buffer = ''
	for chunk in file_obj:
		buffer += chunk
		while buffer:
			try:
				result, index = decoder.raw_decode(buffer)
				yield result
				buffer = buffer[index:]
			except ValueError as e:
				print("1",e)
				 # Not enough data to decode, read more
				break


@never_cache
@login_required(login_url="/login/")
def calendar(request):
	all_bookings = m.Booking.objects.all().filter(booking_status='Approve')
	booking_arr =[]

	for i in all_bookings:
			booking_sub_arr = {}
			booking_sub_arr['title'] = str(i.booking_title)
			# start_date = datetime.datetime.strptime(str(i.startTime), "%Y-%m-%d %H:%M:%S")
			# end_date = datetime.datetime.strptime(str(i.endTime), "%Y-%m-%d %H:%M:%S")
			booking_sub_arr['start'] = datetime.datetime.combine(i.date , i.starttime)
			booking_sub_arr['end'] = datetime.datetime.combine(i.date , i.endtime)
			booking_sub_arr['resourceId'] = str(i.room)
			booking_sub_arr['booked_by'] = str(i.booked_by)
			booking_arr.append(booking_sub_arr)
		#return HttpResponse(json.dumps(booking_arr), content_type='application/json')
	context = Context({
	'booking': booking_arr,
	'pending_request': get_pending_request(request)
	})
	return render(request, 'booking/ViewCalendar.html', context)

@never_cache
@login_required(login_url="/login/")
def view_booking(request):
	all_bookings = m.Booking.objects.all().exclude(booking_status='Cancel').exclude(booking_status='Reject')
	booking_arr =[]

	for i in all_bookings:
			booking_sub_arr = {}
			booking_sub_arr['title'] = str(i.booking_title)
			booking_sub_arr['full_title'] = "ID:" +  str(i.booking_id) + " -  Title:" +  str(i.booking_title) + "  , Status:" + str(i.booking_status) + "  , Room:" + str(i.room.room_type)
			# start_date = datetime.datetime.strptime(str(i.startTime), "%Y-%m-%d %H:%M:%S")
			# end_date = datetime.datetime.strptime(str(i.endTime), "%Y-%m-%d %H:%M:%S")
			booking_sub_arr['start'] = datetime.datetime.combine(i.date , i.starttime)
			booking_sub_arr['end'] = datetime.datetime.combine(i.date , i.endtime)
			booking_sub_arr['resourceId'] = str(i.room)
			booking_sub_arr['booked_by'] = str(i.booked_by)
			booking_sub_arr['status'] = str(i.booking_status)
			booking_arr.append(booking_sub_arr)
		#return HttpResponse(json.dumps(booking_arr), content_type='application/json')

	context = Context({
	'booking': booking_arr,
	'pending_request': get_pending_request(request)
	})
	return render(request, 'booking/ViewBooking.html', context)

class ManageDatatable(Datatable):
	sort_date = columns.DateColumn(source=['date'])
	class Meta:
		model = m.Booking
		columns = ['booking_id','sort_date','date','starttime','endtime','room','booking_status','prioritize','booking_title','booked_by','equipment','confidential','involve','no_of_attendees','attendees']
		ordering = ['date','starttime','endtime','-room']
		processors = {
			'starttime': helpers.format_date('%I:%M %p'),
			'endtime': helpers.format_date('%I:%M %p'),
			'room': helpers.make_xeditable(type="select",source=['S','M','B']),
			'prioritize': helpers.make_xeditable(type="select",source=['Yes','No']),
			'booking_status': helpers.make_xeditable(type="select",source=['Approve','Reject']),
			}

@method_decorator(admin_decorators, name='dispatch')
class manage_booking(XEditableDatatableView):
	template_name = "booking/ManageBooking.html"
	#model  = m.Booking
	datatable_class = ManageDatatable

	def get_queryset(self):
		queryset = m.Booking.objects.extra(where=["(\"Date\" + \"EndTime\") >= (date %s + time %s)","\"Booking_Status\" = \'Approve\' OR \"Booking_Status\" = \'Pending\'"], params=[datetime.datetime.now().date(), datetime.datetime.now().time() ])
		return queryset
	def get_context_data(self, **kwargs):
		context = super(manage_booking, self).get_context_data(**kwargs)
		context['pending_request'] = get_pending_request(self)
		return context

class HistoryDatatable(Datatable):
	sort_date = columns.DateColumn(source=['date'])
	class Meta:
		model = m.Booking
		columns = ['booking_id','sort_date','date','starttime','endtime','room','booking_status','prioritize','booking_title','booked_by','equipment','confidential','involve','no_of_attendees','attendees']
		ordering = ['-date','starttime','endtime']
		processors = {
			'starttime': helpers.format_date('%I:%M %p'),
			'endtime': helpers.format_date('%I:%M %p'),
			}

@method_decorator(decorators, name='dispatch')
class history_booking(DatatableView):
	template_name = "booking/HistoryBooking.html"
	#model  = m.Booking
	datatable_class = HistoryDatatable

	def get_queryset(self):
		queryset = m.Booking.objects.extra(where=["(\"Date\" + \"EndTime\") < (date %s + time %s) OR \"Booking_Status\" = \'Reject\' OR \"Booking_Status\" = \'Cancel\'"], params=[datetime.datetime.now().date(), datetime.datetime.now().time() ])
		return queryset
	def get_context_data(self, **kwargs):
		context = super(history_booking, self).get_context_data(**kwargs)
		context['pending_request'] = get_pending_request(self)
		return context

class MyDatatable(Datatable):
	cancel = columns.TextColumn("Cancel Booking")
	class Meta:
		model = m.Booking
		columns = ['booking_id','date','starttime','endtime','room','booking_title','no_of_attendees','involve','equipment','confidential','booking_status','cancel']
		ordering = ['-date','starttime','endtime']
		processors = {
			'starttime': helpers.format_date('%I:%M %p'),
			'endtime': helpers.format_date('%I:%M %p'),
			}
		

@method_decorator(decorators, name='dispatch')
class my_booking(DatatableView):
	template_name = "booking/MyBooking.html"
	datatable_class = MyDatatable

	def get_queryset(self):
		return m.Booking.objects.filter(booked_by=self.request.user.username)

	def get_context_data(self, **kwargs):
			context = super(my_booking, self).get_context_data(**kwargs)
			context['pending_request'] = get_pending_request(self)
			return context

	def post(self, request, **kwargs): 
		try:
			if request.method=='POST':
				booking_id = request.POST.get('booking_id')
				booking_status = request.POST.get('booking_status')
				cancelation = m.Booking.objects.filter(booking_id=booking_id)
				if cancelation:
					cancelation.update(booking_status = booking_status)
				return HttpResponse("")
		except:
			pass

class ManageUser(Datatable):
	class Meta:
		model = m.AuthUser
		columns = ['username','first_name','email','is_superuser']
		exclude = ['id','password','date_joined','last_login','last_name','is_staff','is_active']
		processors = {'is_superuser': helpers.make_xeditable(type="select",source=['True','False'])}
		labels={'is_superuser': "Admin"}

@method_decorator(admin_decorators, name='dispatch')
class manage_user(XEditableDatatableView):
	template_name = "booking/ManageUser.html"
	model  = m.AuthUser
	datatable_class = ManageUser

	def get_context_data(self, **kwargs):
		context = super(manage_user, self).get_context_data(**kwargs)
		context['pending_request'] = get_pending_request(self)
		return context