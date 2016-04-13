# -*- coding:utf-8 -*-

from datetime import datetime
from django.utils.functional import cached_property
from application.models import Groups, GroupList, Students, Lessons, Passes, Debts, Comments
from application.utils.date_api import get_last_day_of_month, get_count_of_weekdays_per_interval


class GroupLogic(object):

    def __init__(self, group_id, date=None):
        now = datetime.now()

        self.orm = Groups.objects.get(pk=group_id)
        self.date_1 = date or datetime.combine(self.orm.end_date, datetime.min.time()) if self.orm.end_date else datetime(now.year, now.month, 1)
        self.date_2 = self.orm.end_datetime or get_last_day_of_month(now)

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
        return list(Lessons.objects.select_related('group_pass', 'student').filter(group=self.orm, student__in=self.students, date__range=[self.date_1, self.date_2]).order_by('date'))

    @cached_property
    def debts(self):
        return list(Debts.objects.select_related('student').filter(group=self.orm, student__in=self.students))

    @cached_property
    def passes(self):
        return set([l.group_pass for l in self.lessons])

    @cached_property
    def phantom_passes(self):
        return list(Passes.objects.select_related('bonus_class', 'student').filter(
            bonus_class__isnull=False,
            student__in=self.students,
            group=self.orm,
            start_date__isnull=True
        ).order_by('pk'))

    @cached_property
    def calendar(self):
        days = get_count_of_weekdays_per_interval(self.orm.days, self.date_1, self.date_2)
        return self.orm.get_calendar(date_from=self.date_1, count=days, clean=False)

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
