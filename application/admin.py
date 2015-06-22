# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *
from forms import GroupsForm


class GroupAdmin(admin.ModelAdmin):
    form = GroupsForm

admin.site.register(Groups, GroupAdmin)
admin.site.register(PassTypes)