# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *
from forms import GroupsForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserChangeForm
from application.models import User as CustomUser


class GroupAdmin(admin.ModelAdmin):
    form = GroupsForm


class CustomUserChangeForm(UserChangeForm):
    u"""Обеспечивает правильный функционал для поля с паролем и показ полей профиля."""

    password = ReadOnlyPasswordHashField(
        label=u'Password',
        help_text="Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>.")

    def clean_password(self):
        return self.initial["password"]

    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    list_display = (u'username', u'first_name', u'last_name',
                    'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (u'Personal_info', {'fields': (
                'first_name', 'last_name', 'email'
            )}),
        (u'Roles', {'fields': ('is_active', 'is_staff', 'teacher', 'sampo_admin', 'is_superuser', 'user_permissions')}),
        # (u'Dates', {'fields': ('last_login', 'date_joined')}),
        # (u'Groups', {'fields': ('groups',)}),
    )

admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(Groups, GroupAdmin)
admin.site.register(PassTypes)
admin.site.register(DanceHalls)
admin.site.register(Log)
admin.site.register(BonusClasses)
#admin.site.register(SampoPrises)
