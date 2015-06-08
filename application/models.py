# -*- coding: utf-8 -*-

from django.db import models


class Groups(models.Model):

    u"""
    Группы
    """

    name = models.CharField(max_length=100, verbose_name=u'Название группы')
    start_date = models.DateField(verbose_name=u'Дата начала группы')
    teacher_leader = models.ForeignKey(User, verbose_name=u'Преподаватель - партнер', null=True, blank=True, related_name=u'leader')
    teacher_follower = models.ForeignKey(User, verbose_name=u'Преподаватель - партнерша', null=True, blank=True, related_name=u'follower')
    days = models.CharField(max_length=30, verbose_name=u'Дни проведения')
    is_opened = models.BooleanField(verbose_name=u'Группа открыта', default=True)

    def __unicode__(self):

        leader = self.teacher_leader.first_name if self.teacher_leader else ''
        follower = self.teacher_follower.first_name if self.teacher_follower else ''

        return u'%s - %s %s - %s' % (self.name, leader, follower, self.days)

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

    def __unicode__(self):
        return u'%s (%dр.)' % (self.name, self.prise)

    class Meta:
        app_label = u'application'
        verbose_name = u'Тип абонемента'
        verbose_name_plural = u'Типы абонементов'


class Passes(models.Model):

    u"""
    Абонементы
    """

    student = models.ForeignKey(Students, verbose_name=u'Ученик')
    start_date = models.DateField(verbose_name=u'Начало действия абонемента')
    pass_type = models.ForeignKey(PassTypes, verbose_name=u'Абонемент')
    lessons = models.PositiveIntegerField(verbose_name=u'Количество оставшихся занятий')
    skips = models.PositiveIntegerField(verbose_name=u'Количество оставшихся пропусков')

    class Meta:
        app_label = u'application'
        verbose_name = u'Абонемент'
        verbose_name_plural = u'Абонементы'