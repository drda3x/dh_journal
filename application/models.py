# -*- coding: utf-8 -*-

import datetime, math, calendar as calendar_origin
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import utc
from django.contrib.auth.models import User as UserOrigin, UserManager

from application.utils.date_api import get_count_of_weekdays_per_interval
from application.utils.date_api import get_week_offsets_from_start_date, WEEK, get_week_days_names
from application.utils.phones import get_string_val

calendar = calendar_origin.Calendar()


class User(UserOrigin):

    def __unicode__(self):
        return '%s %s' % (self.last_name, self.first_name)

    objects = UserManager
    teacher = models.BooleanField(verbose_name=u'Преподаватель', default=False)
    sampo_admin = models.BooleanField(verbose_name=u'Администратор САМПО', default=False)

    def __short_json__(self):
        return dict(
            first_name=self.first_name,
            last_name=self.last_name
        )

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
    end_date = models.DateField(verbose_name=u'Дата окончания группы', null=True, blank=True, default=None)
    time = models.TimeField(verbose_name=u'Время начала занятия', null=True, blank=True, default=None)
    teacher_leader = models.ForeignKey(User, verbose_name=u'Препод 1', null=True, blank=True, related_name=u'leader')
    teacher_follower = models.ForeignKey(User, verbose_name=u'Препод 2', null=True, blank=True, related_name=u'follower')
    is_opened = models.BooleanField(verbose_name=u'Группа открыта', default=True)
    is_settable = models.BooleanField(verbose_name=u'Набор открыт', default=True)
    _days = models.CommaSeparatedIntegerField(max_length=7, verbose_name=u'Дни')
    _available_passes = models.CommaSeparatedIntegerField(max_length=1000, verbose_name=u'Абонементы', null=True, blank=True)
    dance_hall = models.ForeignKey(DanceHalls, verbose_name=u'Зал')

    @property
    def available_passes(self):
        return self._available_passes.split(',')

    @property
    def days(self):
        return get_week_days_names(self._days.split(','))

    @property
    def days_nums(self):
        return map(int,self._days.split(','))

    @property
    def last_lesson(self):
        now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        _from = datetime.datetime.combine(self.start_date, datetime.datetime.min.time())
        cnt = get_count_of_weekdays_per_interval(self.days, _from, now) + 1
        return self.start_date if now <= _from else filter(lambda x: x <= now, self.get_calendar(cnt))[-1].date()

    def get_calendar(self, count, date_from=None, clean=True):
        start_date = date_from if date_from else self.start_date
        days = calendar.itermonthdays2(start_date.year, start_date.month)

        cur_month_days = map(
            lambda _d: datetime.datetime(start_date.year, start_date.month, _d[0]),
            filter(lambda day: day[0] and day[0] >= start_date.day and day[1] in self.days_nums, days)
        )

        try:
            canceled_lessons = CanceledLessons.objects.filter(group=self, date__gte=start_date).values_list('date', flat=True)

        except CanceledLessons.DoesNotExist:
            canceled_lessons = []

        if clean:
            cur_month_days = filter(lambda day: day.date() not in canceled_lessons, cur_month_days)

        if len(cur_month_days) < count:
            next_month = start_date.month + 1 if start_date.month < 12 else 1
            next_year = start_date.year if start_date.month < 12 else start_date.year + 1

            cur_month_days += self.get_calendar(
                count - len(cur_month_days),
                datetime.datetime(next_year, next_month, 1),
                clean=clean
            )

        res = cur_month_days[:count]

        if not clean:

            _res = []

            for r in res:
                _res.append(
                    {'date': r, 'canceled': r.date() in canceled_lessons} if not isinstance(r, dict) else r
                )

            res = _res

        return res

    @property
    def end_datetime(self):
        return datetime.datetime.combine(self.end_date, datetime.datetime.min.time()) if self.end_date else None

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if not self.is_opened and not self.end_date:
            self.end_date = datetime.datetime.now()
        # elif self.is_opened:
        #     self.end_date = None

        super(Groups, self).save(force_insert, force_update, using, update_fields)

    @property
    def time_repr(self):
        return str(self.time or '')[0:-3]

    def __unicode__(self):

        leader = self.teacher_leader.last_name if self.teacher_leader else ''
        follower = self.teacher_follower.last_name if self.teacher_follower else ''
        days = '-'.join(self.days)

        return u'%s - %s %s - %s %s' % (self.name, leader, follower, days, self.time_repr) + (u' - ЗАКРЫТА' if not self.is_opened else '')

    class Meta:
        app_label = u'application'
        verbose_name = u'Группу'
        verbose_name_plural = u'Группы'


class CanceledLessons(models.Model):
    group = models.ForeignKey(Groups)
    date = models.DateField(verbose_name=u'Дата отмененного урока')

    class Meta:
        app_label = u'application'
        verbose_name = u'Отмененное занятие'
        verbose_name_plural = u'Отмененные занятия'


class Students(models.Model):

    u"""
    Ученики
    """

    first_name = models.CharField(max_length=30, verbose_name=u'Фамилия')
    last_name = models.CharField(max_length=30, verbose_name=u'Имя')
    father_name = models.CharField(max_length=30, verbose_name=u'Отчество', null=True, blank=True)
    phone = models.CharField(verbose_name=u'Телефон', max_length=20)
    e_mail = models.CharField(max_length=30, verbose_name=u'e-mail')
    org = models.BooleanField(verbose_name=u'Орг', default=False)
    is_deleted = models.BooleanField(verbose_name=u'Удален', default=False)

    def __json__(self):
        return dict(
            id=self.pk,
            first_name=self.first_name,
            last_name=self.last_name,
            phone=dict(raw=self.phone, formated=self.str_phone),
            e_mail=self.e_mail,
            org=self.org
        )

    def __unicode__(self):
        return u'%s %s.%s' % (self.first_name, self.last_name[0].upper(), self.father_name[0].upper() if self.father_name else '')

    @property
    def str_phone(self):
        return get_string_val(self.phone)

    class Meta:
        app_label = u'application'
        verbose_name = u'Ученик'
        verbose_name_plural = u'Ученики'


class Debts(models.Model):
    u"""
    Хранилищи записей о долгах
    """

    date = models.DateField(verbose_name=u'Дата')
    student = models.ForeignKey(Students)
    group = models.ForeignKey(Groups)
    val = models.FloatField(verbose_name=u'Сумма')


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
    sequence = models.PositiveIntegerField(verbose_name=u'Порядковый номер', null=True, blank=True)
    shown_value = models.CharField(verbose_name=u'Отображаемое значение(если пустое - показывается цена за занятие)', null=True, blank=True, max_length=30)

    def __unicode__(self):
        return u'%s - %s (%dр.)' % (str(self.sequence), self.name, self.prise)

    def __json__(self):
        return dict(
            name=self.name,
            prise=self.prise,
            lessons=self.lessons,
            skips=self.skips,
            color=self.color,
            oneGroupPass=self.one_group_pass
        )

    def save(self, *args, **kwargs):

        try:
            max_seq = PassTypes.objects.all().aggregate(models.Max('sequence'))['sequence__max'] or 0

        except PassTypes.DoesNotExist:
            max_seq = 0

        if not self.sequence or self.sequence > max_seq:
            self.sequence = max_seq + 1

        else:

            try:
                prev_seq = PassTypes.objects.get(id=self.id).sequence

            except PassTypes.DoesNotExist:
                prev_seq = None

            if prev_seq != self.sequence:
                if prev_seq and self.sequence > prev_seq:
                    _type = PassTypes.objects.filter(sequence__gt=prev_seq).order_by('sequence').first()
                    _type.sequence = prev_seq
                    super(PassTypes, _type).save()

                else:
                    _seq = self.sequence + 1
                    for _type in PassTypes.objects.filter(sequence__gte=self.sequence).exclude(id=self.id).order_by('sequence'):
                        _type.sequence = _seq
                        _seq += 1

                        super(PassTypes, _type).save()

        super(PassTypes, self).save(*args, **kwargs)

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
    active = models.BooleanField(verbose_name=u'Ссылка активна', default=True)

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
    lessons_origin = models.PositiveIntegerField(verbose_name=u'Количество изначально заданных занятий')
    skips_origin = models.PositiveIntegerField(verbose_name=u'Количество изначально заданных пропусков', null=True, blank=True)
    opener = models.ForeignKey(User, null=True, blank=True)
    creation_date = models.DateField(verbose_name=u'Дата содания(оплаты абонемента)', null=True, blank=True, auto_now=True)

    @property
    def one_group_pass(self):
        return self.pass_type.one_group_pass

    @property
    def shown_value(self):
        return self.pass_type.shown_value

    @property
    def date(self):
        return self.frozen_date or self.start_date

    def get_lessons_before_date(self, date):
        return Lessons.objects.filter(group_pass=self, date__lt=date)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.lessons is None:
            self.lessons = self.pass_type.lessons
        if self.skips in [None, '']:
            self.skips = self.pass_type.skips if isinstance(self.pass_type.skips, int) else None

        if self.lessons_origin is None:
            self.lessons_origin = self.pass_type.lessons

        if self.skips_origin in [None, '']:
            self.skips_origin = self.pass_type.skips if isinstance(self.pass_type.skips, int) else None

        super(Passes, self).save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    @property
    def color(self):
        return self.pass_type.color

    @property
    def one_lesson_prise(self):
        return round(float(self.pass_type.prise) / self.pass_type.lessons, 2)

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
    def sign(self):

        if self.status == Lessons.STATUSES['not_processed']:
            return ''
        elif self.status == Lessons.STATUSES['moved']:
            return Lessons.STATUSES_RUS['moved']
        elif self.status == Lessons.STATUSES['attended']:
            return self.group_pass.shown_value or str(self.prise()) + 'р'
        else:
            return '--' + self.group_pass.shown_value if self.group_pass.shown_value else self.prise() * -1

    @property
    def rus(self):
        rev_status = {val: key for key, val in self.STATUSES.iteritems()}
        return self.STATUSES_RUS[rev_status[self.status]]

    def prise(self):
        return self.group_pass.one_lesson_prise

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        now = datetime.datetime.now().date()
        try:
            compared_date = self.date.date()
        except AttributeError:
            compared_date = self.date

        if compared_date > now:
            self.status = Lessons.STATUSES['not_processed']

        super(Lessons, self).save(force_insert, force_update, using, update_fields)

    @cached_property
    def is_first_in_pass(self):
        first_lesson = Lessons.objects.filter(group_pass=self.group_pass).earliest('date')
        return self.group_pass.start_date == self.date

    @cached_property
    def is_last_in_pass(self):
        last_lesson = Lessons.objects.filter(group_pass=self.group_pass).latest('date')
        return last_lesson.date == self.date

    class Meta:
        app_label = u'application'
        verbose_name = u'Журнал посещения'


class SampoPayments(models.Model):

    date = models.DateTimeField(verbose_name=u'Время оплаты')
    staff = models.ForeignKey(User, verbose_name=u'Администратор САМПО')
    people_count = models.PositiveIntegerField(verbose_name=u'Количество людей')
    money = models.IntegerField(verbose_name=u'Сумма')
    comment = models.CharField(verbose_name=u'Коментарий', max_length=50, null=True, blank=True)

    def __str__(self):
        return '%s %s %d' % (self.date.strftime('%d.%m.%Y %H:%M'), self.staff, self.money)

    def __unicode__(self):
        return u'%s %s %d' % (self.date.strftime('%d.%m.%Y %H:%M'), self.staff, self.money)

    def __json__(self):
        return dict(
            date=self.date.strftime('%d.%m.%Y %H:%M'),
            staff=self.staff.__short_json__(),
            people_count=self.people_count,
            money=self.money,
            comment=self.comment
        )

    class Meta:
        app_label = u'application'
        verbose_name = u'Оплата сампо'


class SampoPasses(models.Model):

    name = models.TextField(verbose_name=u'Имя')
    surname = models.TextField(verbose_name=u'фамилия')
    payment = models.ForeignKey(SampoPayments, verbose_name=u'Оплата абонемента')

    def __str__(self):
        return '%s %s %s' % (self.surname, self.name, self.payment)

    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.surname, self.payment)

    def __json__(self):

        return dict(
            id=self.pk,
            name=self.name,
            surname=self.surname,
            payment=self.payment.__json__()
        )

    class Meta:
        app_label = u'application'
        verbose_name = u'Абонементы САМПО'


class SampoPassUsage(models.Model):

    sampo_pass = models.ForeignKey(SampoPasses, verbose_name=u'Абонемент')
    date = models.DateTimeField(verbose_name=u'Время')

    class Meta:
        app_label = u'application'
        verbose_name = u'Отметки о посещении сампо'


class HtmlPaymentsTypes(object):

    ADD = 'text-success'
    WRITE_OFF = 'text-error'
    DEFAULT = ''


class Log(models.Model):

    date = models.DateTimeField(verbose_name=u'Время записи', auto_now=True)
    msg = models.TextField(verbose_name=u'Сообщение', max_length=1000)

    def __unicode__(self):
        return '%s - %s' % (self.date.strftime('%d.%m.%Y %H:%M:%S'), self.msg)


class SampoPrises(models.Model):
    prise = models.PositiveIntegerField(verbose_name=u'Сумма')
    date_from = models.DateField(verbose_name=u'Дата начала действия')
    date_to = models.DateField(verbose_name=u'Дата окончания действия', null=True, blank=True)

    def __unicode__(self):
        return u'c %s по %s (%d)' % (self.date_from.strftime('%d.%m.%Y'), self.date_to.strftime('%d.%m.%Y') if self.date_to else u'не ограничено', self.prise)

    class Meta:
        unique_together = ('date_from', 'date_to')
        app_label = u'application'
        verbose_name = u'Цены на сампо'
        verbose_name_plural= u'Цены на сампо'


class BonusClasses(models.Model):

    date = models.DateField(verbose_name=u'Дата')
    time = models.TimeField(verbose_name=u'Время', null=True, blank=True)
    hall = models.ForeignKey(DanceHalls, verbose_name=u'Зал')
    teacher_leader = models.ForeignKey(User, verbose_name=u'Преподаватель 1', null=True, blank=True, related_name='teacher1')
    teacher_follower = models.ForeignKey(User, verbose_name=u'Преподаватель 2', null=True, blank=True, related_name='teacher2')
    can_edit = models.BooleanField(verbose_name=u'Открыт для редактирования преподавателями', default=True)

    def repr_short(self):
        return u'%s %s' % (self.date.strftime('%d.%m.%Y'), self.hall.station)

    def __unicode__(self):
        return u'%s %s %s %s' % (
            self.date.strftime('%d.%m.%Y'), 
            self.hall.station, 
            self.teacher_leader.last_name if self.teacher_leader else u'', 
            self.teacher_follower.last_name if self.teacher_follower else u''
        )

    class Meta:
        unique_together = ('date', 'hall')
        app_label = u'application'
        verbose_name = u'Мастер-класс'
        verbose_name_plural = u'Мастер-классы'


class BonusClassList(models.Model):

    group = models.ForeignKey(BonusClasses)
    student = models.ForeignKey(Students)
    attendance = models.BooleanField(verbose_name=u'Присутствие', default=False)
    group_pass = models.ForeignKey(Passes, null=True, blank=True)
    active = models.BooleanField(verbose_name=u'Ссылка активна', default=True)

    def update(self, **kwargs):
        for key, val in kwargs.iteritems():
            setattr(self, key, val)
        self.save()

    class Meta:
        unique_together = ('group', 'student')
        app_label = u'application'