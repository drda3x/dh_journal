# -*- coding: utf-8 -*-

import datetime, math
from django.db import models
from django.contrib.auth.models import User

from application.utils.date_api import get_week_offsets_from_start_date, WEEK


class Days(models.Model):
    name = models.CharField(max_length=2)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = u'application'
        verbose_name = u'День недели'
        verbose_name_plural = u'Дни недели'


class Groups(models.Model):

    u"""
    Группы
    """

    name = models.CharField(max_length=100, verbose_name=u'Название группы')
    start_date = models.DateField(verbose_name=u'Дата начала группы')
    teacher_leader = models.ForeignKey(User, verbose_name=u'Препод 1', null=True, blank=True, related_name=u'leader')
    teacher_follower = models.ForeignKey(User, verbose_name=u'Препод 2', null=True, blank=True, related_name=u'follower')
    days = models.ManyToManyField(Days, verbose_name=u'Дни проведения')
    is_opened = models.BooleanField(verbose_name=u'Группа открыта', default=True)
    is_settable = models.BooleanField(verbose_name=u'Набор открыт', default=True)

    def get_calendar(self, count, date_from=None):

        start_date = date_from if date_from else self.start_date

        week_offsets = get_week_offsets_from_start_date(start_date, [i.name for i in self.days.all()])

        first_offset = week_offsets.pop(0)

        if WEEK[start_date.weekday()] in self.days.all().values_list('name', flat=True):
            current_date = start_date

        else:
            current_date = start_date + datetime.timedelta(days=first_offset)

        offset_index = 0

        get_delta = lambda index: datetime.timedelta(days=week_offsets[index])

        while count > 0:

            try:
                delta = get_delta(offset_index)

            except IndexError:
                offset_index = 0
                delta = get_delta(offset_index)

            yield current_date

            current_date = current_date + delta

            count -= 1

            if len(week_offsets) > 1:
                offset_index += 1

    def __unicode__(self):

        leader = self.teacher_leader.last_name if self.teacher_leader else ''
        follower = self.teacher_follower.last_name if self.teacher_follower else ''
        days = ' '.join(map(lambda x: x.name, self.days.all()))
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