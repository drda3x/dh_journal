# -*- coding:utf-8 -*-

import datetime

from django.db.models import Q, Sum
from django.contrib.auth.models import User

from application.utils.passes import get_color_classes
from application.models import Groups, Students, Passes, Lessons, GroupList, Comments, CanceledLessons, Debts
from application.utils.date_api import get_count_of_weekdays_per_interval, get_week_days_names
from application.utils.passes import ORG_PASS_HTML_CLASS


def get_groups_list(user, opened=True):

    u"""
    Получить список групп для конкретного пользоваетля
    """

    if not isinstance(user, User):
        return None

    if user.is_superuser:
        return {
            'self': [
                {'id': g.id, 'name': g.name, 'days': ' '.join(g.days), 'time': g.time_repr , 'orm': g}
                for g in Groups.objects.filter(
                    Q(teacher_leader=user) | Q(teacher_follower=user),
                    Q(is_opened=opened)
                )
            ],
            'other': [
                {'id': g.id, 'name': g.name, 'days': ' '.join(g.days), 't1': g.teacher_leader.last_name if g.teacher_leader else '', 't2':g.teacher_follower.last_name if g.teacher_follower else '', 'time': g.time_repr , 'orm': g}
                for g in Groups.objects.filter(is_opened=opened).exclude(
                    Q(teacher_leader=user) | Q(teacher_follower=user)
                )
            ]
        }

    return {
        'self': [
            {'id': g.id, 'name': g.name, 'days': ' '.join(g.days), 'time': g.time_repr , 'orm': g}
            for g in Groups.objects.filter(
                Q(teacher_leader=user) | Q(teacher_follower=user),
                Q(is_opened=opened)
            )
        ]
    }


def get_group_detail(group_id, _date_from, date_to, date_format='%d.%m.%Y'):

    u"""
    Получить детальную информацию о группе
    """

    group = Groups.objects.get(pk=group_id)

    gs_dt = datetime.datetime.combine(group.start_date, datetime.datetime.min.time())

    date_from = _date_from if gs_dt < _date_from else gs_dt

    dates_count = get_count_of_weekdays_per_interval(
        group.days,
        date_from,
        date_to
    )

    calendar = group.get_calendar(date_from=date_from, count=dates_count, clean=False)

    students = [
        {
            'person': s,
            'calendar': [get_student_lesson_status(s, group, dt) for dt in calendar],  #get_student_calendar(s, group, date_from, dates_count, '%d.%m.%Y'),
            'debt': get_student_total_debt(s, group),
            'pass_remaining': len(get_student_pass_remaining(s, group)),
            'last_comment': Comments.objects.filter(group=group, student=s).order_by('add_date').last()
        } for s in get_group_students_list(group, date_from, date_to)
    ]

    moneys = []
    money_total = {key: 0 for key in ('day_total', 'dance_hall')}

    for _day in calendar:
        buf = dict()

        qs = Lessons.objects.filter(group=group, date=_day['date'])
        flag = qs.exclude(status__in=(Lessons.STATUSES['not_processed'], Lessons.STATUSES['moved'])).exists()

        if not _day['canceled'] and flag:

            buf['day_total'] = reduce(
                lambda _sum, l: _sum + l.prise(),
                qs.exclude(status__in=(Lessons.STATUSES['not_processed'], Lessons.STATUSES['moved'])),
                0
            ) - int(Debts.objects.filter(date=_day['date'], group=group).aggregate(total=Sum('val'))['total'] or 0)

            buf['dance_hall'] = int(group.dance_hall.prise)
            buf['club'] = round((buf['day_total'] - buf['dance_hall']) * 0.3, 0)
            buf['balance'] = round(buf['day_total'] - buf['dance_hall'] - abs(buf['club']), 0)
            buf['half_balance'] = round(buf['balance'] / 2, 1)
            buf['date'] = _day
            buf['canceled'] = False

            for key in money_total.iterkeys():
                money_total[key] += (buf[key] if isinstance(buf[key], (int, float)) else 0)

        else:
            buf['day_total'] = ''
            buf['dance_hall'] = ''
            buf['club'] = ''
            buf['balance'] = ''
            buf['half_balance'] = ''
            buf['date'] = ''
            buf['canceled'] = _day['canceled'] is True

        moneys.append(buf)

    money_total['club'] = round((money_total['day_total'] - money_total['dance_hall']) * 0.3, 0)
    money_total['balance'] = round(money_total['day_total'] - money_total['dance_hall'] - abs(money_total['club']), 0)
    money_total['half_balance'] = round(money_total['balance'] / 2, 1)

    try:
        if buf['balance']:

            money_total['next_month_balance'] = reduce(
                lambda acc, l: acc + l.prise(),
                Lessons.objects.filter(
                    group=group,
                    date__gt=date_to,
                    group_pass__start_date__lt=date_to
                ),
                0
            )

    except Exception:
        from traceback import format_exc
        print format_exc()


    # money = dict()
    # money['dance_hall'] = group.dance_hall.prise
    # money['total'] = reduce(lambda _sum, l: _sum + l.prise(), Lessons.objects.filter(group=group, date__range=[date_from, date_to]).exclude(status=Lessons.STATUSES['moved']), 0)
    # money['club'] = round((money['total'] - money['dance_hall']) * 0.3, 0)
    # money['balance'] = round(money['total'] - money['dance_hall'] - money['club'], 0)

    def to_iso(elem):
        elem['date'] = elem['date'].strftime(date_format)

        return elem

    return {
        'id': group.id,
        'name': group.name,
        'days': group.days,
        'start_date': group.start_date,
        'students': students,
        'last_lesson': group.last_lesson,
        'calendar': map(to_iso, calendar),
        'moneys': moneys,
        'money_total': money_total,
        'full_teachers': group.teacher_leader and group.teacher_follower
    }


def get_student_total_debt(student, group):

    u'''
    Проверить наличие долгов у студента
    :param student: models.Student
    :param group: models.Group
    :return: models.Debt | None
    '''

    try:
        #return Debts.objects.filter(student=student, group=group).aggregate(total_debt=Sum('val'))['total_debt']
        return len(Debts.objects.filter(student=student, group=group))

    except Debts.DoesNotExist:
        return None


def get_student_pass_remaining(student, group):
    passes = Passes.objects.filter(student=student, group=group)
    return [l for p in passes for l in Lessons.objects.filter(group_pass=p, status=Lessons.STATUSES['not_processed'])]


def get_group_students_list(_group, date_from=None, date_to=None):

    u"""
    Получить список учеников из группы
    """

    if not isinstance(_group, Groups) and not isinstance(_group, int) and not isinstance(_group, long):
        raise TypeError('Expected Groups instance or group id!')

    group = _group if isinstance(_group, Groups) else Groups.objects.get(pk=_group)
    group_list_qs = GroupList.objects.filter(group=group, active=True)

    if not group_list_qs.exists():
        return []

    students = Students.objects.filter(
        pk__in=group_list_qs.values('student_id'),
        is_deleted=False
    ).extra(select={
        'active': 1
    }).order_by('last_name', 'first_name')

    if date_from and date_to:
        all_students = Lessons.objects.filter(date__range=[date_from, date_to], group=group).values_list('student_id', flat=True)
        debts = Debts.objects.filter(group=group).values_list('student_id', flat=True)
        active_students = [s.id for s in students]
        return Students.objects.filter(
            Q(Q(pk__in=all_students) | Q(pk__in=active_students) | Q(pk__in=debts))
        ).extra(select={
            'active': 'case when id in (%s) then 1 else 0 end' % ','.join(map(lambda i: str(i), active_students))
        }).order_by('last_name', 'first_name')

    return students


def get_teacher_students_list(teacher):

    u"""
    Получить список учеников конкретного преподавателя
    """

    if not isinstance(teacher, User):
        raise TypeError('Expected User instance!')

    res = []

    for group in Groups.objects.filter(Q(teacher_leader=teacher) | Q(teacher_follower=teacher)):

        res += filter(
            lambda elem: elem not in res,
            get_group_students_list(group)
        )

    return res


def get_student_groups(student, include_closed=False):
    params = dict(student=student)
    if not include_closed:
        params['group__is_opened'] = True

    return [dt.group for dt in GroupList.objects.select_related().filter(**params)]


def get_student_lesson_status(student, group, _date):

    if isinstance(_date, dict):
        date = _date['date']

        if _date['canceled']:
            return {
                'pass': False,
                'color': '',
                'sign': '',
                'attended': False,
                'canceled': True
            }
    elif isinstance(_date, (datetime.datetime, datetime.date)):
        date = _date

    else:
        raise TypeError('wrong arguments')

    try:
        debt = Debts.objects.get(student=student, group=group, date=date)
    except Debts.DoesNotExist:
        debt = None

    try:
        lesson = Lessons.objects.get(student=student, group=group, date=date)

        html_color_classes = {
            key: val for val, key in get_color_classes()
        }

        buf = {
            'pass': True,
            'sign': 'долг' if debt else lesson.sign,
            'sign_type': 's' if debt or isinstance(lesson.sign, str) else 'n',
            'attended': lesson.status == Lessons.STATUSES['attended'],
            'pid': lesson.group_pass.id
        }

        if not lesson.status == Lessons.STATUSES['moved']:

            if not student.org or not lesson.group_pass.pass_type.one_group_pass or lesson.group_pass.pass_type.lessons == 1:
                    buf['color'] = html_color_classes[lesson.group_pass.color]
            else:
                buf['color'] = ORG_PASS_HTML_CLASS

        buf['canceled'] = False

        return buf

    except Lessons.DoesNotExist:
        return {
            'pass': False,
            'color': 'text-error' if debt else '',
            'sign': 'долг' if debt else '',
            'sign_type': 's' if debt else '',
            'attended': False,
            'canceled': False
        }


# def get_student_calendar(student, group, from_date, lessons_count, form=None):
#
#     u"""
#     Получить календарь занятий для конкретного ученика и конкретной ргуппы
#     """
#
#     html_color_classes = {
#         key: val for val, key in get_color_classes()
#     }
#
#     group_calendar = group.get_calendar(date_from=from_date, count=lessons_count)
#     lessons = Lessons.objects.filter(student=student, group=group, date__gte=from_date).order_by('date')
#     lessons_itr = iter(lessons)
#
#     calendar = []
#
#     try:
#         c_lesson = lessons_itr.next()
#
#     except StopIteration:
#         return [
#             {
#                 'date': d if not form else d.strftime(form),
#                 'sign': ''
#             } for d in group_calendar
#         ]
#
#     no_lessons = False
#
#     for c_date in group_calendar:
#
#         buf = {
#             'date': c_date if not form else c_date.strftime(form)
#         }
#
#         if no_lessons or c_lesson.date > c_date.date():
#             buf['pass'] = False
#             buf['color'] = None
#             buf['sign'] = ''
#
#         else:
#             buf['pass'] = True
#             buf['sign'] = c_lesson.rus if not c_lesson.status == Lessons.STATUSES['not_processed'] and c_lesson.date == c_date.date() else ''
#
#             if not student.org or not c_lesson.group_pass.pass_type.one_group_pass or c_lesson.group_pass.pass_type.lessons == 1:
#                 buf['color'] = html_color_classes[c_lesson.group_pass.color]
#             else:
#                 buf['color'] = ORG_PASS_HTML_CLASS
#
#             try:
#                 c_lesson = lessons_itr.next()
#
#             except StopIteration:
#                 no_lessons = True
#
#         calendar.append(buf)
#
#     return calendar
