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


def process_lesson(request):

    json_data = json.loads(request.GET['data'])

    group = Groups.objects.get(pk=json_data['group_id'])
    date = datetime.datetime.strptime(json_data['date'], '%d.%m.%Y')
    data = json_data['data']

    new_passes = filter(lambda p: isinstance(p, dict), data)
    old_passes = filter(lambda p: isinstance(p, int), data)

    attended_passes = []
    attended_passes_ids = []

    if new_passes:
        for p in new_passes:
            pt = PassTypes.objects.get(pk=p['pass_type'])
            st_id = p['student_id']
            if not Passes.objects.filter(student_id=st_id, group=group, pass_type=pt, start_date=date).exists():
                pass_orm_object = Passes(
                    student_id=st_id,
                    group=group,
                    pass_type=pt,
                    start_date=date
                )
                pass_orm_object.save()

                wrapped = PassLogic.wrap(pass_orm_object)
                wrapped.create_lessons(date)

                wrapped.presence = p.get('presence', False)
                attended_passes.append(wrapped)

    if old_passes:
        for p in old_passes:
            pass_orm_object = Passes.objects.select_related().filter(student_id=p, group=group, start_date__lte=date).order_by('start_date').last()
            l_cnt = pass_orm_object.pass_type.lessons
            st_dt = pass_orm_object.start_date
            calendar = group.get_calendar(l_cnt, date_from=st_dt)

            if date in calendar:
                wrapped = PassLogic.wrap(pass_orm_object)
                wrapped.new_pass = False
                attended_passes.append(wrapped)

    for _pass in attended_passes:
        if _pass:
            if not _pass.new_pass or _pass.presence:
                _pass.set_lesson_attended(date, group=group.id)
            attended_passes_ids.append(_pass.orm_object.id)

    for _pass in (PassLogic.wrap(p) for p in Passes.objects.filter(group=group, start_date__lte=date, lessons__gt=0).exclude(pk__in=attended_passes_ids)):
        if _pass:
            _pass.set_lesson_not_attended(date)

    return HttpResponse(200)