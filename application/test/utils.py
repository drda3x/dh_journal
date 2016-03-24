#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from application.models import Groups, GroupList, Students, Passes, PassTypes, DanceHalls


def create_dance_hall():
    dh = DanceHalls(
        prise=1000
    )
    dh.save()

    return dh


def create_pass_type(one_group_pass=True):
    pt = PassTypes(
        name='test_clubcard_pass',
        prise=1000,
        lessons=8,
        one_group_pass=one_group_pass
    )
    pt.save()

    return pt


def create_multipass_type():
    return create_pass_type(False)


def create_pass(_student=None, _group=None, pass_type=None):
    date = datetime.datetime.now()
    student = _student or create_student()
    group = _group or create_group(passes=pass_type)
    assign_student(student, group)

    params = dict(
        start_date=date,
        student=student,
        group=group,
        pass_type=pass_type
    )

    if not pass_type.one_group_pass:
        params['end_date'] = date + datetime.timedelta(days=30)

    group_pass = Passes(**params)
    group_pass.save()

    return group_pass


def create_multipass(student=None, group=None):
    return create_pass(student, group, create_multipass_type())


def create_student():
    student = Students(
        first_name='fn',
        last_name='ln',
        phone='89261112233'
    )
    student.save()

    return student


def create_group(dance_hall=None, _passes=None):

    passes = _passes if hasattr(_passes, '__iter__') else [_passes or create_pass_type()]

    group = Groups(
        name='test_group',
        start_date=datetime.datetime(2016, 1, 1),
        teacher_leader_id=2,
        _days='4,5',
        _available_passes=','.join([str(_pass.pk) for _pass in passes]),
        dance_hall=dance_hall or create_dance_hall()
    )
    group.save()

    return group


def assign_student(group, student):
    if not GroupList.objects.filter(group=group, student=student).exists():
        group_list = GroupList(
            group=group,
            student=student
        )
        group_list.save()