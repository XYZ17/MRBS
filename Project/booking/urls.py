"""booking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import my_booking,manage_booking,history_booking, manage_user, AutocompleteUser
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', views.calendar),
    url(r'^MyBooking/', my_booking.as_view(),  name='my_booking'),
    url(r'^NewBooking/', views.new_booking),
    url(r'^ViewCalendar/', views.calendar),
    url(r'^ViewBooking/', views.view_booking),
    url(r'^ManageBooking/', manage_booking.as_view(),  name='manage_booking'),
    url(r'^HistoryBooking/', history_booking.as_view(),  name='history_booking'),
    url(r'^ManageUser/', manage_user.as_view(),  name='manage_user'),
    url(r'^user-autocomplete/$',AutocompleteUser.as_view(),name='user-autocomplete',
    ),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
