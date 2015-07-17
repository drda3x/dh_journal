# -*- coding:utf-8 -*-

import datetime, json, copy

from django.http.response import HttpResponse, HttpResponseNotFound

from application.utils.lessons import LessonsFactory
from application.utils.passes import PassLogic
from application.models import Students, Passes, Groups, GroupList, PassTypes
from application.views import group_detail_view


# todo Сделать чтобы абонементы не могли пересекаться!!!!!
# todo Сделать расчет последнего занятия
# todo Сделать выбор месяца для группы с начала этой группы
# todo Заменить значок "А" на значок доллара
# todo Добавить поле "Коментарии"
# todo Реализовать логику заморозки, передачи и полного списания абонемента
# todo Реализовать работу списания занятия с дгургого абонемента


def add_student(request):

    first_name = request.GET['first_name']
    last_name = request.GET['last_name']
    phone = request.GET['phone']
    e_mail = request.GET['e_mail']
    group_id = int(request.GET['id'])
    is_org = True if 'is_org' in request.GET.iterkeys() else False

    try:
        student = Students.objects.get(first_name=first_name, last_name=first_name, phone=phone)

        if GroupList.objects.filter(student=student, group_id=group_id).exists():
            return group_detail_view(request)

    except Students.DoesNotExist:
        student = Students(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            e_mail=e_mail,
            org=is_org
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


def edit_student(request):
    return HttpResponseNotFound('Need to realize back-end for this functionality')


def try_to_add_pass(**kwargs):
    try:
        student_id = int(kwargs['student_id'])
        group_id = int(kwargs['group_id'])
        date = kwargs['pass_start_date']
        pass_type_id = int(kwargs['pass_type'])
        presence = kwargs.get('presence', False)

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
                LessonsFactory.create(
                    'attended' if presence and date == lessons_date else 'not_processed',
                    date=lessons_date,
                    group=group,
                    student_id=student_id,
                    group_pass=new_pass,
                ).save()

        return True

    except Exception:
        return False


def process_lesson(request):

    json_data = json.loads(request.GET['data'])

    group_id = json_data['group_id']
    date = datetime.datetime.strptime(json_data['date'], '%d.%m.%Y')
    data = json_data['data']

    new_passes = filter(lambda p: isinstance(p, dict), data)
    old_passes = filter(lambda p: isinstance(p, int), data)

    attended_passes = []
    attended_passes_ids = []

    if new_passes:
        attended_passes += map(
            lambda np: PassLogic.get_or_create(student_id=np['student_id'], group_id=group_id, pass_type=np['pass_type'], date=date),
            new_passes
        )

    if old_passes:
        attended_passes += map(
            lambda p: PassLogic.get_or_create(id=p),
            old_passes
        )

    for _pass in attended_passes:
        _pass.set_lesson_attended(date)
        attended_passes_ids.append(_pass.orm_object.id)

    for _pass in (PassLogic.wrap(p) for p in Passes.objects.filter(group__id=group_id).exclude(pk__in=attended_passes_ids)):
        _pass.set_lesson_not_attended(date)

    return HttpResponse(200)