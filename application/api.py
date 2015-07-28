# -*- coding:utf-8 -*-

import datetime, json, copy

from traceback import format_exc

from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseServerError

from application.utils.passes import PassLogic
from application.models import Students, Passes, Groups, GroupList, PassTypes, Lessons
from application.views import group_detail_view


# todo Сделать чтобы абонементы не могли пересекаться!!!!!
# todo Сделать расчет последнего занятия
# todo Сделать выбор месяца для группы с начала этой группы
# todo Заменить значок "А" на значок доллара
# todo Добавить поле "Коментарии"
# todo Реализовать логику заморозки, передачи и полного списания абонемента
# todo Реализовать работу списания занятия с дгургого абонемента


def add_student(request):

    try:
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

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def delete_student(request):
    student = Students.objects.get(pk=request.GET['student'])
    student.is_deleted = True
    student.save()


def edit_student(request):
    return HttpResponseNotFound('Need to realize back-end for this functionality')


def delete_pass(request):
    try:
        ids = json.loads(request.GET['ids'])
        passes = Passes.objects.filter(pk__in=ids)

        processed = ((p.id, PassLogic.wrap(p).delete()) for p in passes)

        if all([p1[1] for p1 in processed]):
            return HttpResponse(200)

        errors = filter(lambda x: not x[1], processed)
        return HttpResponseServerError(json.dumps(errors))

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def change_pass_owner(request):
    """
    Back-end для передачи абонемента от одного ученика другому
    :param request:
    :return:
    """

    current_owner = request.GET['cur_owner']
    new_owner = request.GET['new_owner']
    ids = json.loads(request.GET['ids'])
    co_pass = Passes.objects.filter(pk__in=ids)

    if not co_pass:
        return HttpResponseServerError('failed')

    changed = map((p.id, PassLogic.wrap(p).change_owner(new_owner, date)) for p in co_pass)

    if all([changed(1)]):
        return HttpResponse(200)

    errors = filter(lambda x: not x[1], changed)

    return HttpResponseServerError(json.dumps(errors))


def write_off_the_pass(request):

    """
    Back-end для списания абонемента
    :param request:
    :return:
    """

    try:
        ids=json.loads(request.GET['ids'])
        passes = Passes.objects.filter(pk__in=ids)
        processed = ((p.id, PassLogic.wrap(p).write_off()) for p in passes)

        if all(p[1] for p in processed):
            return HttpResponse(200)

        errors = filter(lambda x: not x[1], processed)
        return HttpResponseServerError(json.dumps(errors))

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def freeze_pass(request):
    try:
        ids = json.loads(request.GET['ids'])
        group = Groups.objects.get(pk=request.GET['group'])
        date = datetime.datetime.strptime(request.GET['date'], '%d.%m.%Y')
        students = Students.objects.filter(pk__in=ids)

        for student in students:
            p = Passes.objects.filter(student=student, group=group).order_by('start_date').last()

            if p.lessons > 0:
                wrapped = PassLogic.wrap(p)
                wrapped.freeze(date)
            else:
                pass

        return HttpResponse(200)
    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def get_passes(request):
    try:
        owner = request.GET['owner']
        group_id = request.GET['group']
        passes = Passes.objects.filter(student_id=owner, group_id=group_id, lessons__gt=0).order_by('start_date')

        return HttpResponse(
            json.dumps([p.__json__() for p in passes])
        )

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def process_lesson(request):

    """
    Back-end для обработки занятий
    :param request:
    :return:
    """

    try:
        json_data = json.loads(request.GET['data'])

        group = Groups.objects.get(pk=json_data['group_id'])
        date = datetime.datetime.strptime(json_data['date'], '%d.%m.%Y')
        data = json_data['data']
        canceled = json_data['canceled']

        new_passes = filter(lambda p: isinstance(p, dict), data)
        old_passes = filter(lambda p: isinstance(p, int), data)

        attended_passes = []
        attended_passes_ids = []
        error = []
        next_date = group.get_calendar(2, date)[-1]

        if not canceled:
            if new_passes:
                for p in new_passes:
                    pt = PassTypes.objects.get(pk=p['pass_type'])
                    st_id = p['student_id']
                    if pt.lessons > 1 and any(p.date > date.date() for p in Passes.objects.filter(student_id=st_id, group=group, lessons__gt=0, pass_type__one_group_pass=True)):
                        error.append(st_id)
                    elif not Passes.objects.filter(student_id=st_id, group=group, pass_type=pt, start_date=date).exists():
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
                    st_dt = pass_orm_object.date
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
            if _pass and _pass.check_date(date):
                _pass.set_lesson_not_attended(date) if not canceled else _pass.freeze(next_date)

        if error:
            return HttpResponseServerError(json.dumps(error))

        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')