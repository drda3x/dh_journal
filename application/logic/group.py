# -*- coding:utf-8 -*-

from datetime import datetime
from copy import deepcopy
from django.utils.functional import cached_property
from django.db.models import Sum
from application.models import Groups, GroupList, Students, Lessons, Passes, Debts, Comments
from application.utils.date_api import get_last_day_of_month, get_count_of_weekdays_per_interval


class copy_cache(cached_property):
    def __get__(self, instance, type=None):
        return deepcopy(super(copy_cache, self).__get__(instance, type))


class GroupLogic(object):

    def __init__(self, group_id, date=None):
        now = datetime.now()

        self.orm = Groups.objects.select_related('dance_hall').get(pk=group_id)
        self.date_1 = date or (datetime.combine(self.orm.end_date, datetime.min.time()) if self.orm.end_date else datetime(now.year, now.month, 1))
        self.date_2 = self.orm.end_datetime or get_last_day_of_month(self.date_1).replace(hour=23, minute=59, second=59, microsecond=0)
        self.days = get_count_of_weekdays_per_interval(self.orm.days, self.date_1, self.date_2)

    def __getattr__(self, item):
        try:
            return getattr(self, item)
        except Exception:
            return getattr(self.orm, item)

    @cached_property
    def students(self):
        return [obj.student for obj in GroupList.objects.select_related('student').filter(group=self.orm, active=True).order_by('student__last_name').only('student')]

    @cached_property
    def lessons(self):
        return list(Lessons.objects.select_related('group_pass', 'group_pass__pass_type', 'student').filter(group=self.orm, student__in=self.students, date__range=[self.date_1, self.date_2]).order_by('date'))

    @cached_property
    def debts(self):
        return list(Debts.objects.select_related('student').filter(group=self.orm, student__in=self.students))

    @cached_property
    def passes(self):
        return set([l.group_pass for l in self.lessons])

    def get_pass_lessons(self, _pass):
        return [l for l in self.lessons if l.group_pass == _pass]

    @cached_property
    def phantom_passes(self):
        return list(Passes.objects.select_related('bonus_class', 'student').filter(
            bonus_class__isnull=False,
            student__in=self.students,
            group=self.orm,
            start_date__isnull=True
        ).order_by('pk'))

    @copy_cache
    def calendar(self):
        return self.orm.get_calendar(date_from=self.date_1, count=self.days, clean=False)

    @cached_property
    def comments(self):
        return list(Comments.objects.select_related('student').filter(group=self.orm, student__in=self.students).order_by('add_date'))

    @cached_property
    def last_lesson_ever(self):
        try:
            return Lessons.objects.filter(group=self.orm).latest('date')
        except Lessons.DoesNotExist:
            return None

    def get_students_net(self):
        net = []

        for student in self.students:
            lessons = filter(lambda l: l.student == student, self.lessons)
            lessons_dates = [l.date for l in lessons]
            debts = filter(lambda d: d.student == student and d.date not in lessons_dates, self.debts)
            phantom_passes = filter(lambda p: p.student == student, self.phantom_passes)
            comments = filter(lambda c: c.student == student, self.comments)

            _net = []
            arr = lessons + debts
            arr.sort(key=lambda x: x.date)

            for p in phantom_passes:
                try:
                    temp_date = arr[-1].date if arr[-1].date > self.orm.last_lesson else self.orm.last_lesson
                except IndexError:
                    temp_date = self.orm.last_lesson

                dd = p.bonus_class.date if p.bonus_class.date > temp_date else temp_date
                for phantom_lesson in self.orm.get_calendar(p.lessons, dd):
                    arr.append(self.PhantomLesson(phantom_lesson.date(), p))

            iterator = iter(arr)
            i_calendar = iter(self.calendar)

            try:
                obj = iterator.next()
                for date in i_calendar:
                    if date['canceled']:
                        _net.append(self.CanceledLesson())
                    elif obj.date == date['date'].date():
                        _net.append(obj)
                        obj = iterator.next()
                    else:
                        _net.append(None)

            except StopIteration:
                _net += [None] * len(list(i_calendar))

            net.append(
                dict(
                    student=student,
                    lessons=_net,
                    pass_remaining=len(filter(lambda l: l.status == Lessons.STATUSES['not_processed'], lessons)),
                    last_comment=comments[-1] if comments else None
                )
            )

        return net

    def calc_money(self):
        saldo = []
        total = 0
        total_rent = 0
        statuses = [Lessons.STATUSES['attended'], Lessons.STATUSES['not_attended']]
        for day in self.calendar:
            buf = {}
            lessons = filter(lambda _l: _l.date == day['date'].date() and _l.status in statuses, self.lessons)

            if lessons:
                day_saldo = sum(
                    map(lambda l: l.prise(), lessons),
                    0
                )

                buf['day_total'] = day_saldo
                buf['dance_hall'] = int(self.orm.dance_hall.prise)
                buf['club'] = round((buf['day_total'] - buf['dance_hall']) * 0.3, 0)
                buf['balance'] = round(buf['day_total'] - buf['dance_hall'] - abs(buf['club']), 0)
                buf['half_balance'] = round(buf['balance'] / 2, 1)
                buf['date'] = day['date']
                buf['canceled'] = day['canceled']

                total += buf['day_total']
                total_rent += buf['dance_hall']

            else:
                buf['day_total'] = ''
                buf['dance_hall'] = ''
                buf['club'] = ''
                buf['balance'] = ''
                buf['half_balance'] = ''
                buf['date'] = ''
                buf['canceled'] = day['canceled']

            saldo.append(buf)

        totals = dict()
        totals['day_total'] = sum(map(lambda x: x['day_total']or 0, saldo))
        totals['dance_hall'] = total_rent #todo если отмена занятий, то возможно денег списывать не надо!
        totals['club'] = round((totals['day_total'] - totals['dance_hall']) * 0.3, 0)
        totals['balance'] = round(totals['day_total'] - totals['dance_hall'] - totals['club'], 0)
        totals['half_balance'] = round(totals['balance'] / 2, 1)
        totals['next_month_balance'] = -1000

        try:
            if filter(lambda dt: not dt['canceled'], self.calendar)[-1]['date'].date() <= self.orm.last_lesson:
                totals['next_month_balance'] = sum(map(
                    lambda l: l.prise(),
                    list(Lessons.objects.filter(
                        group=self.orm,
                        date__gt=self.calendar[-1]['date'],
                        group_pass__creation_date__lte=self.calendar[-1]['date']
                    ))
                ))
        except IndexError:
            pass

        return saldo, totals

    class PhantomLesson(object):

        def __init__(self, date, group_pass):
            self.date = date
            self.group_pass = group_pass

    class CanceledLesson(object):
        pass


"""

from application.models import Groups as G
gr = G.opened.first()
from application.logic.group import GroupLogic as GL
gl = GL(6)
n = gl.get_students_net()
for i in n:
    print i

"""
