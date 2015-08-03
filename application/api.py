# -*- coding:utf-8 -*-

import datetime, json, copy

from traceback import format_exc

from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.db.models import Q

from application.utils.passes import PassLogic
from application.utils.groups import get_group_students_list
from application.utils.phones import check_phone
from application.models import Students, Passes, Groups, GroupList, PassTypes, Lessons, User, Comments, CanceledLessons
from application.views import group_detail_view


# todo Сделать чтобы абонементы не могли пересекаться!!!!!
# todo Сделать расчет последнего занятия
# todo Сделать выбор месяца для группы с начала этой группы
# todo Заменить значок "А" на значок доллара
# todo Добавить поле "Коментарии"
# todo Реализовать логику заморозки, передачи и полного списания абонемента
# todo Реализовать работу списания занятия с дгургого абонемента


def edit_user_profile(request):

    try:
        uid = request.POST['uid']
        user_name = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        phone = check_phone(request.POST.get('phone', None))
        email = request.POST.get('email', None)
        old_password = request.POST.get('old_pass', None)
        password = request.POST.get('pass', None)
        password_confirm = request.POST.get('pass_conf', None)

        user = User.objects.get(pk=uid)

        if password and password_confirm:
            if not old_password or not user.check_password(old_password):
                return HttpResponseServerError('Введен неправильный текущий пароль')
            elif password != password_confirm:
                return HttpResponseServerError('Новый пароль не совпадает с подтвержением')

        elif (password and not password_confirm) or (password_confirm and not password):
            return HttpResponseServerError('Новый пароль не совпадает с подтвержением')

        user.username =user_name
        user.first_name = first_name
        user.last_name = last_name
        if email:
            user.email = email
        if password:
            user.set_password(password)

        user.save()

        return HttpResponse(200)
    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def add_student(request):

    try:
        first_name = request.GET['first_name']
        last_name = request.GET['last_name']
        phone = check_phone(request.GET['phone'])
        e_mail = request.GET['e_mail']
        group_id = int(request.GET['id'])
        is_org = request.GET['is_org'] == u'true'

        try:
            student = Students.objects.get(first_name=first_name, last_name=last_name, phone=phone)

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

        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def delete_student(request):
    try:
        ids = json.loads(request.GET['ids'])
        students = Students.objects.filter(pk__in=ids)
        errors = []
        for student in students:
            try:
                student.is_deleted = True
                student.save()

            except Exception:
                errors.append(student.id)

        return HttpResponse(200) if not errors else HttpResponseServerError(json.dumps(errors))

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def edit_student(request):
    try:
        student = Students.objects.get(pk=request.GET['stid'])
        student.first_name = request.GET['first_name']
        student.last_name = request.GET['last_name']
        student.phone = check_phone(request.GET['phone'])
        student.e_mail = request.GET.get('e_mail', None)
        student.org = request.GET['is_org'] == u'true'
        student.save()

        return HttpResponse(200)
    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


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
    try:
        current_owner = request.GET['cur_owner']
        new_owner = request.GET['new_owner']
        group = request.GET['group']
        co_pass = Passes.objects.filter(group_id=group, student_id=current_owner, lessons__gt=0)

        if not co_pass:
            return HttpResponseServerError('failed')

        changed = ((p.id, PassLogic.wrap(p).change_owner(new_owner)) for p in co_pass)

        if all(c[1] for c in changed):
            return HttpResponse(200)

        errors = filter(lambda x: not x[1], changed)

        return HttpResponseServerError(json.dumps(errors))

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


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


def get_pass_by_owner(request):
    try:
        pid = request.GET.get('pid', None)
        if not pid:
            sign = request.GET['str'].lower()
            group = Groups.objects.get(pk=request.GET['group'])
            students = filter(lambda x: sign in x.first_name.lower() or sign in x.last_name.lower(), get_group_students_list(group))
            passes = Passes.objects.filter(group=group, student__in=students, lessons__gt=0, pass_type__one_group_pass=True)
        else:
            passes = Passes.objects.filter(pk=pid)

        result = [
            {
                'pass_id': p.id,
                'st_name': p.student.last_name,
                'st_fam': p.student.first_name,
                'lessons': p.lessons
            }
            for p in passes
        ]
        return HttpResponse(json.dumps(result))

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
                    _pt = int(p['pass_type'])
                    if _pt == -1:

                        another_person_pass = Passes.objects.get(pk=p['from_another'])
                        pass_orm_object = Passes(
                            student_id=p['student_id'],
                            group=group,
                            pass_type=another_person_pass.pass_type,
                            start_date=date,
                            lessons=1,
                            skips=0
                        )

                        pass_orm_object.save()
                        wrapped = PassLogic.wrap(pass_orm_object)
                        wrapped.create_lessons(date)

                        another_person_pass.lessons -= 1
                        another_person_pass.save()
                        Lessons.objects.filter(group_pass=another_person_pass).order_by('date').last().delete()
                        attended_passes.append(wrapped)

                    elif 'pass_id' in p.iterkeys():
                        pid = p['pass_id']
                        pass_orm_object = Passes.objects.get(pk=pid)
                        wrapped = PassLogic.wrap(pass_orm_object)
                        attended_passes.append(wrapped)

                    else:
                        pt = PassTypes.objects.get(pk=_pt)
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
                    pass_orm_object = Passes.objects.select_related().filter(
                        Q(student_id=p),
                        Q(group=group),
                        Q(Q(start_date__lte=date) | Q(frozen_date__lte=date))
                    ).order_by('start_date').last()

                    if pass_orm_object:
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

        else:
            CanceledLessons(group=group, date=date).save()

        for _pass in (PassLogic.wrap(p) for p in Passes.objects.filter(
                Q(group=group),
                Q(Q(start_date__lte=date) | Q(frozen_date__lte=date)),
                Q(lessons__gt=0)
        ).exclude(pk__in=attended_passes_ids)):
            if _pass and _pass.check_date(date):
                _pass.set_lesson_not_attended(date) if not canceled else _pass.freeze(next_date)

        if error:
            return HttpResponseServerError(json.dumps(error))

        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def add_or_edit_comment(request):

    def to_json(elem):
        return {
            'id': elem.id,
            'date': elem.add_date.strftime('%d.%m.%Y %H:%M:%S'),
            'msg': elem.text
        }

    cid = request.GET.get('cid', None)
    msg = request.GET.get('msg', None)

    if not msg:
        return HttpResponseServerError('No message')

    try:
        if not cid:
            comment = Comments(
                student=Students.objects.get(pk=request.GET['stid']),
                group=Groups.objects.get(pk=request.GET['group_id']),
                add_date=datetime.datetime.now(),
                text=msg
            )
            comment.save()

        else:
            comment = Comments.objects.get(pk=cid)
            comment.text = msg
            comment.save()

        return HttpResponse(json.dumps({'data': to_json(comment)}))

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def delete_comment(request):

    cid = request.GET.get('cid', None)

    try:
        Comments.objects.get(pk=cid).delete()
        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def get_comments(request):

    def to_json(elem):
        return {
            'id': elem.id,
            'date': elem.add_date.strftime('%d.%m.%Y %H:%M:%S'),
            'msg': elem.text
        }

    try:
        data = map(to_json, Comments.objects.filter(group_id=request.GET['group_id'], student_id=request.GET['stid']).order_by('-add_date'))
        return HttpResponse(json.dumps({'data': data}))

    except Comments.DoesNotExist:
        HttpResponse(json.dumps({'data': []}))

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')
