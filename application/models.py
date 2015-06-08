# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Groups(models.Model):

    u"""
    Группы
    """

    name = models.CharField(max_length=100, verbose_name=u'Название группы')
    start_date = models.DateTimeField(verbose_name=u'Дата начала группы')
    teacher_leader = models.ForeignKey(User, verbose_name=u'Преподаватель - партнер', null=True, blank=True)
    teacher_follower = models.ForeignKey(User, verbose_name=u'Преподаватель - партнерша', null=True, blank=True)
    days = models.CharField(max_length=30, verbose_name=u'Дни проведения')

    def __unicode__(self):

        leader = self.teacher_leader.first_name if self.teacher_leader else ''
        follower = self.teacher_follower.first_name if self.teacher_follower else ''

        return '%s - %s %s - %s' % (self.name, leader, follower, self.days)