# -*- coding: utf-8 -*-

import datetime, math, calendar as calendar_origin
from django.db import models
from django.contrib.auth.models import User

from application.utils.date_api import get_week_offsets_from_start_date, WEEK, get_week_days_names

calendar = calendar_origin.Calendar()

class Groups(models.Model):

    u"""
    Группы
    """

    name = models.CharField(max_length=100, verbose_name=u'Название группы')
    start_date = models.DateField(verbose_name=u'Дата начала группы')
    teacher_leader = models.ForeignKey(User, verbose_name=u'Препод 1', null=True, blank=True, related_name=u'leader')
    teacher_follower = models.ForeignKey(User, verbose_name=u'Препод 2', null=True, blank=True, related_name=u'follower')
    is_opened = models.BooleanField(verbose_name=u'Группа открыта', default=True)
    is_settable = models.BooleanField(verbose_name=u'Набор открыт', default=True)
    _days = models.CommaSeparatedIntegerField(max_length=7, verbose_name=u'Дни')

    @property
    def days(self):
        return get_week_days_names(self._days.split(','))

    @property
    def days_nums(self):
        return map(int,self._days.split(','))

    def get_calendar(self, count, date_from=None):
        start_date = date_from if date_from else self.start_date
        days = calendar.itermonthdays2(start_date.year, start_date.month)
        cur_month_days = map(
            lambda _d: datetime.datetime(start_date.year, start_date.month, _d[0]),
            filter(lambda day: day[0] and day[0] >= start_date.day and day[1] in self.days_nums, days)
        )

        if len(cur_month_days) < count:
            next_month = start_date.month + 1 if start_date.month < 12 else 1
            next_year = start_date.year if start_date.month < 12 else start_date.year + 1

            days1 = calendar.itermonthdays2(next_year, next_month)
            cur_month_days += map(
                lambda _d: datetime.datetime(next_year, next_month, _d[0]),
                filter(lambda day: day[0] and day[1] in self.days_nums, days1)[:count - len(cur_month_days)]
            )

        return cur_month_days[:count]

    def __unicode__(self):

        leader = self.teacher_leader.last_name if self.teacher_leader else ''
        follower = self.teacher_follower.last_name if self.teacher_follower else ''
        days = '-'.join(self.days)
        return u'%s - %s %s - %s' % (self.name, leader, follower, days)

    class Meta:
        app_label = u'application'
        verbose_name = u'Группу'
        verbose_name_plural = u'Группы'


class Students(models.Model):

    u"""
    Ученики
    """

    first_name = models.CharField(max_length=30, verbose_name=u'Фамилия')
    last_name = models.CharField(max_length=30, verbose_name=u'Имя')
    father_name = models.CharField(max_length=30, verbose_name=u'Отчество', null=True, blank=True)
    phone = models.IntegerField(verbose_name=u'Телефон')
    e_mail = models.CharField(max_length=30, verbose_name=u'e-mail')
    org = models.BooleanField(verbose_name=u'Орг', default=False)

    def __unicode__(self):
        return u'%s %s.%s' % (self.first_name, self.last_name[0].upper(), self.father_name[0].upper())

    class Meta:
        app_label = u'application'
        verbose_name = u'Ученик'
        verbose_name_plural = u'Ученики'


class PassTypes(models.Model):

    u"""
    Типы Абонементов
    """

    name = models.CharField(max_length=100, verbose_name=u'Наименование')
    prise = models.PositiveIntegerField(verbose_name=u'Цена')
    lessons = models.PositiveIntegerField(verbose_name=u'Количество занятий')
    skips = models.PositiveIntegerField(verbose_name=u'Количество пропусков', null=True, blank=True)
    color = models.CharField(verbose_name=u'Цвет', max_length=7, null=True, blank=True)

    def __unicode__(self):
        return u'%s (%dр.)' % (self.name, self.prise)

    class Meta:
        app_label = u'application'
        verbose_name = u'Тип абонемента'
        verbose_name_plural = u'Типы абонементов'


class GroupList(models.Model):

    u"""
    Список группы
    """

    group = models.ForeignKey(Groups, verbose_name=u'Группа')
    student = models.ForeignKey(Students, verbose_name=u'Ученик')

    class Meta:
        app_label = u'application'
        verbose_name = u'Список группы'
        verbose_name_plural = u'Списки групп'
        unique_together = ('group', 'student')


class Passes(models.Model):

    u"""
    Абонементы
    """

    student = models.ForeignKey(Students, verbose_name=u'Ученик')
    group = models.ManyToManyField(Groups, verbose_name=u'Группа', null=True, blank=True)
    start_date = models.DateField(verbose_name=u'Начало действия абонемента')
    pass_type = models.ForeignKey(PassTypes, verbose_name=u'Абонемент', null=True, blank=True, default=None)
    lessons = models.PositiveIntegerField(verbose_name=u'Количество оставшихся занятий')
    skips = models.PositiveIntegerField(verbose_name=u'Количество оставшихся пропусков')

    @property
    def color(self):
        return self.pass_type.color

    @property
    def one_lesson_prise(self):
        return self.pass_type.prise / self.pass_type.lessons

    class Meta:
        app_label = u'application'
        verbose_name = u'Абонемент'
        verbose_name_plural = u'Абонементы'


class Lessons(models.Model):

    u"""
    Посещения занятий
    """

    date = models.DateField(verbose_name=u'Дата занятия')
    group = models.ForeignKey(Groups, verbose_name=u'Группа')
    student = models.ForeignKey(Students, verbose_name=u'Учение')
    group_pass = models.ForeignKey(Passes, verbose_name=u'Абонемент', related_name=u'lesson_group_pass')
    presence_sign = models.BooleanField(verbose_name=u'Отметка о присутствии', default=False)

    class Meta:
        app_label = u'application'
        verbose_name = u'Журнал посещения'