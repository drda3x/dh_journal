# -*- coding:utf-8 -*-

import datetime

from application.models import Students, Passes
from application.views import group_detail_view


def add_student_to_group(request):

    first_name = request.GET['first_name']
    last_name = request.GET['last_name']
    phone = request.GET['phone']
    e_mail = request.GET['e_mail']
    group_id = request.GET['id']

    try:
        student = Students.objects.get(first_name=first_name, last_name=first_name, phone=phone)
        print student.first_name
    except Students.DoesNotExist:
        student = Students(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            e_mail=e_mail
        )

        student.save()

    student_pass = Passes(
        student=student,
        group_id=group_id,
        start_date=datetime.date.today(),
        lessons=0,
        skips=0
    )

    student_pass.save()

    return group_detail_view(request)