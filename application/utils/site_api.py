# -*- coding:utf-8 -*-

import datetime

from django.http.response import HttpResponse

from application.models import Students, Passes, Groups, GroupList, PassTypes, Lessons
from application.views import group_detail_view


def add_student_to_group(request):

    first_name = request.GET['first_name']
    last_name = request.GET['last_name']
    phone = request.GET['phone']
    e_mail = request.GET['e_mail']
    group_id = request.GET['id']

    try:
        student = Students.objects.get(first_name=first_name, last_name=first_name, phone=phone)

    except Students.DoesNotExist:
        student = Students(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            e_mail=e_mail
        )

        student.save()

    group_list = GroupList(
        student=student,
        group_id=group_id
    )

    try:
        group_list.save()

    except Exception:
        pass

    return group_detail_view(request)


def add_pass(request):

    student_id = int(request.GET['student_id'])
    group_id = int(request.GET['pass_group'])
    date = datetime.datetime.strptime(
        request.GET['pass_start_date'],
        '%d.%m.%Y'
    )
    pass_type_id = int(request.GET['pass_type'])

    if not Passes.objects.filter(student__id=student_id, group__id=group_id, start_date=date.date()).exists():

        pass_type = PassTypes.objects.get(pk=pass_type_id)
        group = Groups.objects.get(pk=group_id)

        new_pass = Passes(
            student_id=student_id,
            start_date=date,
            pass_type=pass_type,
            lessons=pass_type.lessons,
            skips=pass_type.skips
        )

        new_pass.save()

        new_pass.group.add(group)

        for lessons_date in group.get_calendar(date_from=date, count=new_pass.lessons):
            lesson = Lessons(
                date=date,
                group=group,
                student_id=student_id,
                group_pass=new_pass
            )

            lesson.save()

    return HttpResponse()