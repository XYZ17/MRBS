from django.contrib import admin
from . import models
"""
class LDAPGroupAdmin(admin.ModelAdmin):
    exclude = ['dn', 'objectClass']
    list_display = ['user_id', 'user_name', 'user_name']

admin.site.register(models.LDAPGroup, LDAPGroupAdmin)
"""