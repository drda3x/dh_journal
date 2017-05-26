# -*- coding:utf-8 -*-

from datetime import datetime, timedelta, date as dtdate
from copy import deepcopy
from django.utils.functional import cached_property
from django.db.models import Sum, Q, Count
from application.models import Groups, GroupList, Students, Lessons, Passes, Debts, Comments, TeachersSubstitution, BonusClasses
from application.utils.date_api import get_last_day_of_month, get_count_of_weekdays_per_interval
from itertools import chain, takewhile
from collections import Counter


class copy_cache(cached_property):
    def __get__(self, instance, type=None):
        return deepcopy(super(copy_cache, self).__get__(instance, type))


class GroupLogic(object):

    ASSISTANT_SALARY = 500
    MIN_LESSON_SALARY = 625
    DEFAULT_LESSONS_PER_MONTH = 8

    def __init__(self, group, date=None):
        now = datetime.now()

        if isinstance(group, int):
            self.orm = Groups.all.select_related('dance_hall').get(pk=group)
        elif isinstance(group, Groups):
            self.orm = group
        else:
            raise Exception('Expected Groups instance or Groups.id')

        # group_start_date = datetime.combine(self.orm.start_date, datetime.min.time())
        # group_end_date = self.orm_end_date

        self.date_1 = max(date or datetime(now.year, now.month, 1), self.orm.start_datetime)

        if self.orm.end_datetime:

            min_date_1 = get_last_day_of_month(self.date_1).replace(hour=23, minute=59, second=59, microsecond=0)
            min_date_2 = datetime.combine(self.last_lesson_ever.date, datetime.max.time()) \
                if self.last_lesson_ever \
                else self.orm.end_datetime

            self.date_2 = min(min_date_1, min_date_2)
        else:
            self.date_2 = get_last_day_of_month(self.date_1).replace(hour=23, minute=59, second=59, microsecond=0)

        self.days = get_count_of_weekdays_per_interval(self.orm.days, self.date_1, self.date_2)

    def __getattr__(self, item):
        try:
            return getattr(self, item)
        except Exception:
            return getattr(self.orm, item)

    @cached_property
    def students(self):
        return map(
            lambda s: setattr(s.student, 'active', 1) or s.student,
            GroupList.objects.select_related('student').filter(
                Q(active=True) | Q(student__in=set([lesson.student for lesson in self.lessons])),
                group=self.orm, student__is_deleted=False).order_by('student__last_name', 'student__first_name'
            ).only('student')
        )

    @cached_property
    def newbies(self):
        return [st.student_id for st in GroupList.objects.select_related('student').filter(group=self.orm, active=True, last_update__gte=datetime.now() - timedelta(days=14))]

    @cached_property
    def lessons(self):
        return list(Lessons.objects.select_related('group_pass', 'group_pass__pass_type', 'student').filter(group=self.orm, date__range=[self.date_1, self.date_2]).order_by('date'))

    @cached_property
    def all_available_lessons(self):
        return dict(Lessons.objects.filter(group=self.orm, student__in=self.students, status=Lessons.STATUSES['not_processed']).values_list('student').annotate(available_lessons=Count('student')))

    @cached_property
    def debts(self):
        return list(Debts.objects.select_related('student').filter(group=self.orm))#, date__range=[self.date_1, self.date_2]))

    @cached_property
    def passes(self):
        return set([l.group_pass for l in self.lessons])

    def lesson_is_last_in_pass(self, lesson):
        for _p in self.passes:
            if _p == lesson.group_pass:
                return _p.last_lesson_date == lesson.date

    def lesson_is_first_in_pass(self, lesson):
        for _p in self.passes:
            if _p == lesson.group_pass:
                return _p.first_lesson_date == lesson.date

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
        return sorted(
            set(
                [i['date'].date() for i in self.calcked_calendar] + [i.date for i in self.lessons] + [i.date for i in self.debts if self.date_1.date() <= i.date <= self.date_2.date()]
            )
        )

    @copy_cache
    def calcked_calendar(self):
        return self.orm.get_calendar(date_from=self.date_1, count=self.days, clean=False)

    @cached_property
    def canceled_lessons(self):
        return [i['date'].date() for i in self.orm.get_calendar(date_from=self.date_1, count=self.days, clean=False) if i['canceled']]

    @cached_property
    def comments(self):
        return list(Comments.objects.select_related('student').filter(group=self.orm, student__in=self.students).order_by('add_date'))

    @cached_property
    def last_lesson_ever(self):
        try:
            return Lessons.objects.filter(group=self.orm).latest('date')
        except Lessons.DoesNotExist:
            return None

    @cached_property
    def substitutions(self):
        result = dict.fromkeys(self.calendar, list(self.orm.teachers.all()))
        for subst in TeachersSubstitution.objects.filter(group=self.orm, date__range=(self.date_1, self.date_2)).order_by('date'):
            result[subst.date] = list(subst.teachers.all())

        return result

    @cached_property
    def bonus_classes(self):
        now = datetime.now()
        return list(
            BonusClasses.objects.filter(within_group=self.orm, date__range=[self.date_1, now])
        )

    def calc_bonus_class_finance(self, day):
        try:
            bonus_class = filter(lambda bk: bk.date == day, self.bonus_classes).pop(0)
            raw_sum = bonus_class.get_finance()
        except Exception:
            return 0

    def get_students_net(self):
        net = []
        today = datetime.utcnow().date()

        for student in self.students:
            lessons = filter(lambda l: l.student == student, self.lessons)
            lessons_dates = [l.date for l in lessons]
            debts = filter(lambda d: d.student == student and d.date not in lessons_dates and d.date >= self.date_1.date(), self.debts)
            phantom_passes = filter(lambda p: p.student == student, self.phantom_passes)
            comments = filter(lambda c: c.student == student, self.comments)

            _net = []
            arr = lessons + debts
            arr.sort(key=lambda x: x.date)

            for p in phantom_passes:
                last_group_lesson = self.orm.last_lesson
                last_lesson_by_passes = arr[-1].date if len(arr) > 0 else dtdate(1900, 1, 1)
                temp_date = max(p.bonus_class.date, last_group_lesson, last_lesson_by_passes )

                phantom_lessons = [
                    self.PhantomLesson(pl.date(), p)
                    for pl in self.orm.get_calendar(p.lessons, temp_date)
                    if self.date_1 <= pl <= self.date_2
                ]

                arr += phantom_lessons

            iterator = iter(arr)
            i_calendar = iter(self.calendar)

            try:
                obj = iterator.next()
                for date in i_calendar:

                    while obj.date < date:
                        obj = iterator.next()

                    if date in self.canceled_lessons:
                        _net.append(self.CanceledLesson())
                    elif obj.date == date:
                        _net.append(obj)
                        obj = iterator.next()
                    else:
                        _net.append(None)

            except StopIteration:
                _net += [None] * len(list(i_calendar))

            net.append(
                dict(
                    student=student,
                    #debts=[debt for debt in self.debts if debt.student==student],
                    debts = debts,
                    lessons=_net,
                    pass_remaining=self.all_available_lessons.get(student.pk, 0) + sum([p.lessons for p in phantom_passes], 0),
                    comments=comments
                )
            )

        return net

    def calc_money(self):
        saldo = []
        total = 0
        total_rent = 0
        statuses = [Lessons.STATUSES['attended'], Lessons.STATUSES['not_attended']]
        teachers = set(chain(*self.substitutions.itervalues()))
        teachers_count = len(self.orm.teachers.all())

        open_lessons = dict((
            (bc.date, bc)
            for bc in self.bonus_classes
        ))

        for day in self.calendar:
            buf = {}
            open_lesson = open_lessons.get(day)

            lessons = [
                l for l in self.lessons
                if l.date == day and l.status in statuses
            ]

            if open_lesson:
                bonus_class_lessons_to_minus = sum([
                    lesson.prise() for lesson in lessons if lesson.group_pass.bonus_class == open_lesson
                ])

            if lessons or open_lesson:
                day_saldo = sum(
                    [l.prise() for l in lessons], 0
                )

                open_lesson_saldo = (open_lesson.get_finance() - bonus_class_lessons_to_minus)  if open_lesson else None

                buf['day_total'] = day_saldo + (open_lesson_saldo or 0)
                buf['open_lesson'] = open_lesson_saldo if open_lesson else '-'
                buf['dance_hall'] = int(self.orm.dance_hall.prise)
                buf['club'] = round(max(buf['day_total'] - buf['dance_hall'], 0) * 0.3, 0)
                buf['balance'] = round(
                    buf['day_total'] - buf['dance_hall'] - abs(buf['club']),
                    0
                )
                # buf['half_balance'] = round(
                #     max(buf['balance'] / (teachers), 0),
                #     1
                # )
                buf['date'] = day.strftime('%d.%m.%Y')
                buf['canceled'] = [i.strftime('%d.%m.%Y') for i in self.canceled_lessons]

                total += buf['day_total']
                total_rent += buf['dance_hall']

                buf['salary'] = dict.fromkeys([i.pk for i in teachers], 0)
                today_teachers = self.substitutions[day]
                assistants = len(filter(lambda x: x.assistant, today_teachers))

                for t in today_teachers:
                    key = int(t.pk)
                    if t.assistant:
                        buf['salary'][key] = self.ASSISTANT_SALARY
                    elif assistants:
                        buf['salary'][key] = buf['balance'] - self.ASSISTANT_SALARY * assistants
                    else:
                        buf['salary'][key] = buf['balance'] / len(today_teachers)
            else:
                buf['day_total'] = ''
                buf['open_lesson'] = ''
                buf['dance_hall'] = ''
                buf['club'] = ''
                buf['balance'] = ''
                buf['half_balance'] = ''
                buf['date'] = ''
                buf['canceled'] = [i.strftime('%d.%m.%Y') for i in self.canceled_lessons]
                buf['salary'] = dict.fromkeys([i.pk for i in teachers], '')

            saldo.append(buf)

        teacher_lessons_count = Counter(reduce(
            lambda arr, x: arr + x,
            self.substitutions.values(),
            []
        ))

        group_lessons_per_month = len(self.calendar)
        standart_lessons_cnt = 8
        min_lessons_to_compensation = 7 \
            if group_lessons_per_month >= standart_lessons_cnt \
            else (group_lessons_per_month - 1)


        compensation_to = [
            teacher
            for teacher, lessons in teacher_lessons_count.items()
            if not teacher.assistant and lessons >= min_lessons_to_compensation
        ]

        totals = dict()
        totals['day_total'] = sum(map(lambda x: x['day_total'] or 0, saldo))
        totals['dance_hall'] = total_rent #todo если отмена занятий, то возможно денег списывать не надо!
        totals['club'] = round(
            max(totals['day_total'] - totals['dance_hall'], 0) * 0.3,
            0
        )
        totals['balance'] = round(totals['day_total'] - totals['dance_hall'] - totals['club'], 0)
        # totals['half_balance'] = round(
        #     max(totals['balance'] / teachers, 0),
        #     1
        # )
        totals['next_month_balance'] = -1000
        totals['salary'] = dict([
            (int(teacher.pk), {"count": 0, "compensation": 0})
            for teacher in teachers
        ])

        for i in (_i for _i in saldo if type(_i['day_total']) != str ):
            for k in totals['salary'].iterkeys():
                if k in i['salary']:
                    totals['salary'][int(k)]['count'] += i['salary'][int(k)]

        try:
            if sorted(set(self.calendar) - set(self.canceled_lessons))[-1] <= self.orm.last_lesson:
                totals['next_month_balance'] = sum(map(
                    lambda l: l.prise(),
                    list(Lessons.objects.filter(
                        Q(Q(group_pass__creation_date__lte=self.calendar[-1]) | Q(group_pass__in=self.passes)),
                        group=self.orm,
                        date__gt=self.calendar[-1]
                    ))
                ))

                min_month_salary = min(self.MIN_LESSON_SALARY * (len(self.calendar) - len(self.canceled_lessons)), 5000)

                for teacher, salary in totals['salary'].iteritems():
                    compensation_value = min_month_salary - salary['count']
                    if compensation_value > 0 and teacher in compensation_to:
                        totals['salary'][int(teacher.pk)]['compensation'] = compensation_value

        except IndexError:
            pass

        return saldo, totals

    def profit(self):
        u"""
        Прибыльность группы
        """
        teachers_cnt = len(self.orm.teachers.all().exclude(assistant=True))
        assistants = len(self.orm.teachers.filter(assistant=True))
        normal_profit = 650
        good_profit = 1000

        money, _ = self.calc_money()
        vals = [
            m['balance'] / teachers_cnt - self.ASSISTANT_SALARY * assistants if m['balance'] != '' else ''
            for m in money
        ]

        profit = [
            (
                day,
                -1 if val <= normal_profit else 0 if val <= good_profit else 1
            )
            for val, day in zip(vals, self.calendar)
            if val != ''
        ]

        return profit

    @cached_property
    def rt_profit(self):
        default_days = 3
        teachers_cnt = len(self.orm.teachers.all().exclude(assistant=True))
        assistants = len(self.orm.teachers.filter(assistant=True))
        normal_profit = 650
        good_profit = 1000

        money, _ = self.calc_money()
        profit_vals = [
            m['balance'] / teachers_cnt - self.ASSISTANT_SALARY * assistants
            for m in money
            if isinstance(m['balance'], (int, float))
        ][-default_days:]

        profit = sum(profit_vals)

        if len(profit_vals) == 0:
            return 0

        return -1 if profit <= normal_profit * len(profit_vals) else 0 if profit <= good_profit * len(profit_vals) else 1


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
