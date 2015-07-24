# -*- coding:utf-8 -*-

import datetime

from django.db.models import Q
from django.contrib.auth.models import User

from application.utils.passes import get_color_classes
from application.models import Groups, Students, Passes, Lessons, GroupList
from application.utils.date_api import get_count_of_weekdays_per_interval, get_week_days_names
from application.utils.passes import ORG_PASS_HTML_CLASS


def get_groups_list(user):

    u"""
    Получить список групп для конкретного пользоваетля
    """

    if not isinstance(user, User):
        return None

    return [
        {'id': g.id, 'name': g.name, 'days': ' '.join(g.days)}
        for g in Groups.objects.filter(
            Q(teacher_leader=user) | Q(teacher_follower=user)
        )
    ]


def get_group_detail(group_id, date_from, date_to):

    u"""
    Получить детальную информацию о группе
    """

    group = Groups.objects.get(pk=group_id)

    dates_count = get_count_of_weekdays_per_interval(
        group.days,
        date_from,
        date_to
    )

    students = [
        {
            'person': s,
            'calendar': get_student_calendar(s, group, date_from, dates_count, '%d.%m.%Y'),
            'pass_remaining': len(get_student_pass_remaining(s, group))
        } for s in get_group_students_list(group)
    ]

    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)
    last_lesson = filter(lambda x: x <= now, group.get_calendar(date_from=week_ago, count=4))[-1].date()

    return {
        'id': group.id,
        'name': group.name,
        'days': group.days,
        'start_date': group.start_date,
        'students': students,
        'last_lesson': last_lesson,
        'calendar': map(lambda d: d.strftime('%d.%m.%Y'), group.get_calendar(date_from=date_from, count=dates_count))
    }


def get_student_pass_remaining(student, group):
    passes = Passes.objects.filter(student=student, group=group)
    return [l for p in passes for l in Lessons.objects.filter(group_pass=p, status=Lessons.STATUSES['not_processed'])]


def get_group_students_list(group):

    u"""
    Получить список учеников из группы
    """

    if not isinstance(group, Groups):
        raise TypeError('Expected Groups instance!')

    return Students.objects.filter(
        pk__in=GroupList.objects.filter(group=group).values('student_id'),
        is_deleted=False
    )


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


def get_student_calendar(student, group, from_date, lessons_count, form=None):

    u"""
    Получить календарь занятий для конкретного ученика и конкретной ргуппы
    """

    html_color_classes = {
        key: val for val, key in get_color_classes()
    }

    group_calendar = group.get_calendar(date_from=from_date, count=lessons_count)
    lessons = list(Lessons.objects.filter(student=student, group=group, date__gte=from_date))

    multi_passes = Passes.objects.select_related().filter(
        Q(student=student),
        Q(lessons__gt=0),
        Q(pass_type__one_group_pass=False),
        Q(Q(start_date__range=[group_calendar[0], group_calendar[-1]]) | Q(end_date__range=[group_calendar[0], group_calendar[-1]]))
    )

    for p in multi_passes:
        last_lesson = Lessons.objects.filter(group=group, group_pass=p).order_by('date').last()
        for l in group.get_calendar(date_from=last_lesson.date if last_lesson else from_date, count=p.lessons):
            lessons.append(Lessons(student=student, group=group, date=l.date(), group_pass=p))

    lessons.sort(key=lambda x: x.date)
    lessons_itr = iter(lessons)

    calendar = []

    try:
        c_lesson = lessons_itr.next()

    except StopIteration:
        return [
            {
                'date': d if not form else d.strftime(form),
                'sign': ''
            } for d in group_calendar
        ]

    no_lessons = False

    for c_date in group_calendar:

        buf = {
            'date': c_date if not form else c_date.strftime(form)
        }

        if no_lessons or c_lesson.date > c_date.date():
            buf['pass'] = False
            buf['color'] = None
            buf['sign'] = ''

        else:
            buf['pass'] = True
            buf['sign'] = c_lesson.rus if not c_lesson.status == Lessons.STATUSES['not_processed'] and c_lesson.date == c_date.date() else ''
            buf['color'] = html_color_classes[c_lesson.group_pass.color] if not student.org else ORG_PASS_HTML_CLASS

            try:
                c_lesson = lessons_itr.next()

            except StopIteration:
                no_lessons = True

        calendar.append(buf)

    return calendar