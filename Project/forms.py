from django import forms
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth import authenticate, logout,login
from django.forms import ModelForm, DateField, TimeField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple,SelectDateWidget
from datetimewidget.widgets import DateWidget, TimeWidget
import datetime
from dateutil.relativedelta import relativedelta
from dal import autocomplete

class LoginForm(AuthenticationForm):
	login_user = forms.CharField(widget=forms.TextInput(attrs={'class' : 'login-field', 'placeholder': 'Username'}))
	login_pass = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'login-field', 'placeholder': 'Password'}))

class BookingForm(forms.Form): 
	TodayDate = datetime.datetime.now().date()
	DateOptions = {'format': 'yyyy-mm-dd','startDate': TodayDate.strftime("%Y-%m-%d"), 'todayHighlight': True, 'pickerPosition':"bottom-left"}
	EndDateOptions = {'format': 'yyyy-mm-dd','startDate': TodayDate.strftime("%Y-%m-%d")}
	TimeOptions = {'format': 'HH:ii P','startDate': '9999-12-31 07:00' ,'showMeridian' : True, 'minuteStep' : 10 }
	prefer_date = forms.DateField(widget=DateWidget(bootstrap_version=3, options = DateOptions), initial=datetime.date.today())
	end_date = forms.DateField(widget=DateWidget(bootstrap_version=3, options = EndDateOptions))
	start_time = forms.TimeField(widget=TimeWidget(bootstrap_version=3, options = TimeOptions))
	end_time = forms.TimeField(widget=TimeWidget(bootstrap_version=3, options = TimeOptions))
	title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
	choice_list = range(1,41)
	choice_list = ["---------"] + choice_list
	no_of_attendees = forms.ChoiceField(choices=[(i, i) for i in choice_list],widget=forms.Select(attrs={'class':'form-control'}))
	#attendees = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','rows': "1"}),required=False)
	attendees = forms.CharField(widget=autocomplete.Select2Multiple(url='user-autocomplete',forward=['attendees']),required=False)
	involves = forms.ChoiceField(widget=forms.RadioSelect(), choices=[('Internal','Internal Only'), ('External','External')])
	equipments = forms.MultipleChoiceField(widget=CheckboxSelectMultiple(), choices=[('Video','Video Conference'),('Computer','Computer Usage'),('Phone','Phone Conference')], required=False)
	highly_confidential = forms.ChoiceField(choices=[('No', 'No'),('Yes', 'Yes')], widget=forms.Select(attrs={'class':'form-control'}))
