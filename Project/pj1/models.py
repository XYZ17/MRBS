# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Booking(models.Model):
    booking_id = models.CharField(db_column='Booking_ID', primary_key=True, max_length=-1)  # Field name made lowercase.
    booking_dscp = models.TextField(db_column='Booking_Dscp', blank=True, null=True)  # Field name made lowercase.
    booking_datetime = models.DateTimeField(db_column='Booking_DateTime')  # Field name made lowercase.
    booked_starttime = models.TimeField(db_column='Booked_StartTime')  # Field name made lowercase.
    booked_endtime = models.TimeField(db_column='Booked_EndTime')  # Field name made lowercase.
    booked_date = models.DateField(db_column='Booked_Date')  # Field name made lowercase.
    booked_by = models.ForeignKey('User', models.DO_NOTHING, db_column='Booked_By')  # Field name made lowercase.
    booking_status = models.NullBooleanField(db_column='Booking_Status')  # Field name made lowercase.
    user = models.ForeignKey('User', models.DO_NOTHING, db_column='User_ID')  # Field name made lowercase.
    room = models.ForeignKey('Meetingroom', models.DO_NOTHING, db_column='Room_ID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Booking'


class Meetingroom(models.Model):
    room_id = models.TextField(db_column='Room_ID', primary_key=True)  # Field name made lowercase. This field type is a guess.
    room_type = models.CharField(db_column='Room_Type', max_length=50)  # Field name made lowercase.
    room_dscp = models.TextField(db_column='Room_Dscp', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MeetingRoom'


class User(models.Model):
    user_id = models.CharField(db_column='User_ID', primary_key=True, max_length=50)  # Field name made lowercase.
    user_name = models.CharField(db_column='User_Name', max_length=-1)  # Field name made lowercase.
    user_email = models.CharField(db_column='User_Email', max_length=320)  # Field name made lowercase.
    user_password = models.CharField(db_column='User_Password', max_length=100)  # Field name made lowercase.
    user_post = models.CharField(db_column='User_Post', max_length=-1, blank=True, null=True)  # Field name made lowercase.
    user_office = models.SmallIntegerField(db_column='User_Office')  # Field name made lowercase.
    user_isactive = models.BooleanField(db_column='User_isActive')  # Field name made lowercase.
    user_isadmin = models.BooleanField(db_column='User_isAdmin')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
