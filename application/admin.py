# -*- coding: utf-8 -*-

import datetime
from django.contrib import admin
from django.db.models import Q
from models import *
from forms import GroupsForm, BonusClassesForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserChangeForm
from application.models import User as CustomUser, PassTypes


class GroupsAdminStatusFilter(admin.SimpleListFilter):
    title = u'Статусы'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('opened', 'Только открытые'),
            ('closed', 'Только закрытые')
        )

    def queryset(self, request, queryset):
        sets = dict(
            opened=queryset.filter(Q(end_date__isnull=True) | Q(end_date__gte=datetime.datetime.now().date())),
            closed=queryset.filter(end_date__lt=datetime.datetime.now().date())
        )
        # import ipdb; ipdb.set_trace()
        return sets.get(self.value(), queryset)


class GroupsAdminHallFilter(admin.SimpleListFilter):
    title = u'Залы'
    parameter_name = 'hall'

    def lookups(self, *args, **kwargs):
        return (
            ('hall%d' % i.pk, i)
            for i in set(g.dance_hall for g in Groups.objects.all())
        )

    def queryset(self, request, queryset):
        sets = dict(
            (
                (key, queryset.filter(dance_hall=val)) for key, val in self.lookups()
            )
        )
        return sets.get(self.value(), queryset)


class PassTypesFilter(admin.SimpleListFilter):
    title = u"Статусы"
    parameter_name = "pass_type_status"

    def lookups(self, request, model_admin):
        return (
            ('used', u'Только используемые'),
            ('unused', u'Только не используемые')
        )

    def queryset(self, request, queryset):

        sets = dict(
            used=queryset.filter(is_actual=True),
            unused=PassTypes.all.filter(is_actual=False)
        )

        return sets.get(self.value(), PassTypes.all.all())


class PassTypesAdmin(admin.ModelAdmin):
    list_filter = (PassTypesFilter,)
    list_display = (u'name', u'prise', u'lessons', u'actuality')

    def actuality(self, obj):
        return u'Используемый' if obj.is_actual else u'Не используемый'

    actuality.short_description = u'Статус'


class GroupAdmin(admin.ModelAdmin):
    form = GroupsForm
    list_display = (u'name', 'status', u'start_date', '_end_date', u'dance_hall', 'teachers_to_string', u'external_available')
    filter_horizontal = ('teachers', 'available_passes', 'external_passes')
    list_filter = (GroupsAdminStatusFilter, GroupsAdminHallFilter)

    def status(self, obj):
        return u'Открыта' if obj.is_opened else u'Закрыта'

    def teachers_to_string(self, obj):
        return ', '.join(map(str, obj.teachers.all()))

    def _end_date(self, obj):
        return obj.end_date or u'-'

    status.short_description = u'Статус'
    teachers_to_string.short_description = u'Преподаватели'
    _end_date.short_description = u'Дата окончания группы'


class FutureBonusClasses(admin.SimpleListFilter):
    title = u'Состояние'
    parameter_name = 'available'

    def lookups(self, request, model_admin):
        return (
            ('future', u'Будущие'),
            ('past', u'Прошедшие')
        )

    def queryset(self, request, queryset):
        now = datetime.datetime.now().date()
        sets = dict(
            future=queryset.filter(date__gte=now),
            past=queryset.filter(date__lt=now)
        )

        return sets.get(self.value(), queryset)


class BonusClassAdmin(admin.ModelAdmin):
    form = BonusClassesForm
    list_display = ('date', 'hall', 'time', 'teachers_to_string')
    filter_horizontal = ('teachers', 'available_groups', 'available_passes')
    list_filter = (FutureBonusClasses, )

    def teachers_to_string(self, obj):
        return ', '.join(map(str, obj.teachers.all()))

    teachers_to_string.short_description = u'Преподаватели'


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
                'first_name', 'last_name', 'email', 'about', 'photo', 'video'
            )}),
        (u'Roles', {'fields': ('is_active', 'is_staff', 'teacher', 'assistant', 'sampo_admin', 'is_superuser', 'user_permissions')}),
        # (u'Dates', {'fields': ('last_login', 'date_joined')}),
        # (u'Groups', {'fields': ('groups',)}),
    )



admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Groups, GroupAdmin)
admin.site.register(PassTypes, PassTypesAdmin)
admin.site.register(DanceHalls)
admin.site.register(Log)
admin.site.register(BonusClasses, BonusClassAdmin)
admin.site.register(GroupLevels)
admin.site.register(Dances)
#admin.site.register(SampoPrises)
