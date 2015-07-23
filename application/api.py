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

    group_id = json_data['group_id']
    date = datetime.datetime.strptime(json_data['date'], '%d.%m.%Y')
    data = json_data['data']

    new_passes = filter(lambda p: isinstance(p, dict), data)
    old_passes = filter(lambda p: isinstance(p, int), data)

    attended_passes = []
    attended_passes_ids = []

    if new_passes:
        for p in new_passes:
            ptid = np['pass_type']
            if not Passes.objects.get(student_id=student_id, group_id=group_id, pass_type_id=ptid, start_date=date).exists():
                pass_orm_object = Passes(
                    student_id=student_id,
                    group_id=group_id,
                    pass_type_id=ptid,
                    start_date=date
                )
                pass_orm_object.save()
                wraped = PassLogic.wrap(pass_orm_object)
                wraped.create_lessons()
                attended_passes.append(wraped)

    if old_passes:
        for p in old_passes:
            # Выбираем последний абонемент, который начался до даты текущего урока + проверяем что он актуален

    for _pass in attended_passes:
        if _pass:
            if not _pass.new_pass or hasattr(_pass, 'presence') and _pass.presence:
                _pass.set_lesson_attended(date, group=group_id)
            attended_passes_ids.append(_pass.orm_object.id)

    for _pass in (PassLogic.wrap(p) for p in Passes.objects.filter(group__id=group_id, lessons__gt=0).exclude(pk__in=attended_passes_ids)):
        if _pass:
            _pass.set_lesson_not_attended(date)

    return HttpResponse(200)