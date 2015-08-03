# -*- coding: utf-8 -*-

import datetime, math, calendar as calendar_origin
from django.db import models
from django.contrib.auth.models import User as UserOrigin, UserManager

from application.utils.date_api import get_week_offsets_from_start_date, WEEK, get_week_days_names
from application.utils.phones import get_string_val

calendar = calendar_origin.Calendar()


class User(UserOrigin):

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)

    objects = UserManager

    class Meta:
        app_label = u'application'
        verbose_name = u'Преподаватель'
        verbose_name_plural = u'Преподаватели'


class DanceHalls(models.Model):
    """
    Зал
    """

    station = models.CharField(max_length=50, verbose_name=u'Станция метро')
    prise = models.PositiveIntegerField(verbose_name=u'Цена')

    def __unicode__(self):
        return self.station

    class Meta:
        app_label = u'application'
        verbose_name = u'Зал'
        verbose_name_plural = u'Залы'


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
    dance_hall = models.ForeignKey(DanceHalls, verbose_name=u'Зал')

    @property
    def days(self):
        return get_week_days_names(self._days.split(','))

    @property
    def days_nums(self):
        return map(int,self._days.split(','))

    @property
    def last_lesson(self):
        now = datetime.datetime.now()
        week_ago = now - datetime.timedelta(days=7)
        return filter(lambda x: x <= now, self.get_calendar(date_from=week_ago, count=4))[-1].date()

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

            cur_month_days += self.get_calendar(count - len(cur_month_days), datetime.datetime(next_year, next_month, 1))

        return cur_month_days[:count]

    def __unicode__(self):

        leader = self.teacher_leader.last_name if self.teacher_leader else ''
        follower = self.teacher_follower.last_name if self.teacher_follower else ''
        days = '-'.join(self.days)

        return u'%s - %s %s - %s' % (self.name, leader, follower, days) + (u' - ЗАКРЫТА' if not self.is_opened else '')

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
    is_deleted = models.BooleanField(verbose_name=u'Удален', default=False)

    def __unicode__(self):
        return u'%s %s.%s' % (self.first_name, self.last_name[0].upper(), self.father_name[0].upper())

    @property
    def str_phone(self):
        return get_string_val(self.phone)

    class Meta:
        app_label = u'application'
        verbose_name = u'Ученик'
        verbose_name_plural = u'Ученики'


class Comments(models.Model):
    u"""
    Хранилице коментов
    """

    add_date = models.DateTimeField(verbose_name=u'Дата добавления')
    student = models.ForeignKey(Students)
    group = models.ForeignKey(Groups)
    text = models.TextField(max_length=100, verbose_name=u'Текст коментария')

    class Meta:
        app_label = u'application'
        verbose_name = u'Коментарий'
        verbose_name_plural = u'Коментарии'


class PassTypes(models.Model):

    u"""
    Типы Абонементов
    """

    name = models.CharField(max_length=100, verbose_name=u'Наименование')
    prise = models.PositiveIntegerField(verbose_name=u'Цена')
    lessons = models.PositiveIntegerField(verbose_name=u'Количество занятий')
    skips = models.PositiveIntegerField(verbose_name=u'Количество пропусков', null=True, blank=True)
    color = models.CharField(verbose_name=u'Цвет', max_length=7, null=True, blank=True)
    one_group_pass = models.BooleanField(verbose_name=u'Одна группа', default=True)

    def __unicode__(self):
        return u'%s (%dр.)' % (self.name, self.prise)

    def __json__(self):
        return dict(
            name=self.name,
            prise=self.prise,
            lessons=self.lessons,
            skips=self.skips,
            color=self.color,
            oneGroupPass=self.one_group_pass
        )

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
    # group = models.ManyToManyField(Groups, verbose_name=u'Группа', null=True, blank=True)
    group = models.ForeignKey(Groups, verbose_name=u'Группа', null=True, blank=True)
    start_date = models.DateField(verbose_name=u'Начало действия абонемента')
    end_date = models.DateField(verbose_name=u'Окончание действия абонемента', null=True, blank=True)
    pass_type = models.ForeignKey(PassTypes, verbose_name=u'Абонемент', null=True, blank=True, default=None)
    lessons = models.PositiveIntegerField(verbose_name=u'Количество оставшихся занятий')
    skips = models.PositiveIntegerField(verbose_name=u'Количество оставшихся пропусков', null=True, blank=True)
    frozen_date = models.DateField(verbose_name=u'Дата окончания заморозки', null=True, blank=True)

    @property
    def date(self):
        return self.frozen_date or self.start_date

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.lessons is None:
            self.lessons = self.pass_type.lessons
        if self.skips is None:
            self.skips = self.pass_type.skips
        super(Passes, self).save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    @property
    def color(self):
        return self.pass_type.color

    @property
    def one_lesson_prise(self):
        return self.pass_type.prise / self.pass_type.lessons

    def __json__(self):
        return dict(
            id=self.id,
            student=self.student.id,
            group=self.group.id,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date,
            pass_type=self.pass_type.__json__(),
            lessons=self.lessons,
            skips=self.skips,
            color=self.color
        )

    class Meta:
        app_label = u'application'
        verbose_name = u'Абонемент'
        verbose_name_plural = u'Абонементы'


class Lessons(models.Model):

    u"""
    Посещения занятий
    """

    STATUSES = {
        'not_processed': 0,
        'attended': 1,
        'not_attended': 2,
        'frozen': 3,
        'moved': 4,
        'written_off': 5
    }
    STATUSES_RUS = {
        'not_processed': u'не обработано',
        'attended': u'был(а)',
        'not_attended': u'не был(а)',
        'frozen': u'заморожен',
        'moved': u'пропуск',
        'written_off': u'списан'
    }
    DEFAULT_STATUS = STATUSES['not_processed']

    date = models.DateField(verbose_name=u'Дата занятия')
    group = models.ForeignKey(Groups, verbose_name=u'Группа')
    student = models.ForeignKey(Students, verbose_name=u'Учение')
    group_pass = models.ForeignKey(Passes, verbose_name=u'Абонемент', related_name=u'lesson_group_pass')
    status = models.IntegerField(verbose_name=u'Статус занятия', choices=[(val, key) for key, val in STATUSES.iteritems()], default=DEFAULT_STATUS)

    @property
    def rus(self):
        rev_status = {val: key for key, val in self.STATUSES.iteritems()}
        return self.STATUSES_RUS[rev_status[self.status]]

    def prise(self):
        return self.group_pass.one_lesson_prise

    class Meta:
        app_label = u'application'
        verbose_name = u'Журнал посещения'