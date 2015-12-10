# -*- coding:utf-8 -*-

import datetime, json

from pytz import UTC, timezone
from django.utils.timezone import make_aware
from project.settings import TIME_ZONE
from traceback import format_exc
from copy import deepcopy

from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.db.models import Q

from application.utils.passes import PassLogic
from application.utils.groups import get_group_students_list, get_student_lesson_status, get_student_groups
from application.utils.phones import check_phone
from application.utils.date_api import get_count_of_weekdays_per_interval
from application.models import Students, Passes, Groups, GroupList, PassTypes, Lessons, User, Comments, CanceledLessons, Debts, SampoPayments, SampoPasses, SampoPassUsage
from application.views import group_detail_view
from application.system_api import get_models
from application.auth import auth_decorator
from application.utils.sampo import get_sampo_details, write_log

from application.system_api import delete_lessons as _delete_lessons


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
        first_name = request.GET['first_name'].replace(' ', '')
        last_name = request.GET['last_name'].replace(' ', '')
        phone = check_phone(request.GET['phone'])
        e_mail = request.GET['e_mail'].replace(' ', '') if 'e_mail' in request.GET.iterkeys() else None
        group_id = int(request.GET['id'])
        is_org = request.GET.get('is_org') == u'true'

        try:
            student = Students.objects.get(first_name=first_name, last_name=last_name, phone=phone)
            group_list = GroupList.objects.get(student=student, group_id=group_id)

        except Students.DoesNotExist:
            student = Students(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                e_mail=e_mail,
                org=is_org
            )

            student.save()

            group_list = None

        except GroupList.DoesNotExist:
            group_list = None

        if not group_list:
            group_list = GroupList(
                student=student,
                group_id=group_id
            )
            group_list.save()

        elif not group_list.active:
            group_list.active = True
            group_list.save()

        else:
            return HttpResponseServerError('PersonExistedError')

        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def restore_student(request):
    try:
        ids = json.loads(request.GET['ids'])
        gid = request.GET['gid']
        students = Students.objects.filter(pk__in=ids)
        errors = []

        GroupList.objects.filter(group__id=gid, student__id__in=ids).update(active=True)
        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def delete_student(request):
    try:
        ids = json.loads(request.GET['ids'])
        gid = request.GET['gid']
        students = Students.objects.filter(pk__in=ids)
        errors = []

        GroupList.objects.filter(group__id=gid, student__id__in=ids).select_related('student').update(active=False)

        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def edit_student(request):
    #todo При изменении данных ученика нужно проверить их уникальность.
    #todo если окажется что данные не уникальны - нужно переписать все данные об абонементах,
    #todo посещениях и вообще всем где есть student на один id-шник.

    #todo comments
    #todo debts
    #todo grouplist
    #todo lessons
    #todo passes

    #todo нужно создать пред-деплойный скрипт, который пройдет по всем моделям приложения
    #todo и сделает список моделей у которых есть поле "студент" дабы не заниматься этим при обреботке запроса

    try:

        student = Students.objects.get(pk=request.GET['stid'])
        phone = check_phone(request.GET['phone'])
        first_name = request.GET['first_name'].replace(' ', '')
        last_name = request.GET['last_name'].replace(' ', '')

        if not phone:
            raise TypeError('Phone must be a number')

        # Проверить наличие такого же тлефона
        try:
            same_phone_people = Students.objects.filter(phone=phone).exclude(pk=student.id)
            change_list = []
            errors = []

            for human in same_phone_people:

                # Если есть совпадение по имени, фамилии и номеру телефона - добавляем запись в список на изменение
                if human.first_name.lower() == first_name.lower() and human.last_name.lower() == last_name.lower():
                    change_list.append(human)

                else:
                    errors.append(human)

            # В списке на изменение что-то есть - проходим по всем моделям у которых есть ForeinKey на Students и
            # меняем записи для собранного change_list'a
            if change_list:
                models = get_models(Students)
                
                for human in change_list:
                    human_backup = deepcopy(human)
                    back_up = []  # список для сохранения предыдущих состояний базы.

                    try:
                        for model in models:
                            cls = model[1]
                            field_name = model[0]
                            params = {field_name: human}
                            records = cls.objects.filter(**params)

                            for record in records:
                                back_up.append(deepcopy(record))
                                setattr(record, field_name, student)
                                record.save()

                        human.delete()

                    except Exception:
                        # Если одно из сохранений провалилось - восстанавливаем предыдущее состояние
                        # для всех записей конкретного человека
                        for record in back_up:
                            record.save()

                        human_backup.save()

            # В списке людей с одинаковыми именами и телефонами что-то есть.
            # выдаем информацию об этимх записях
            if errors:
                pass

        # Совпадений нет
        except Students.DoesNotExist:
            pass

        student.first_name = first_name
        student.last_name = last_name
        student.phone = phone
        student.e_mail = request.GET.get('e_mail', None)
        student.org = request.GET['is_org'] == u'true'
        student.save()

        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def delete_lessons(request):
    try:
        params = json.loads(request.GET['params'])
        date = datetime.datetime.strptime(params[0], '%d.%m.%Y')
        count = int(params[1])
        result = _delete_lessons(request.GET['gid'], request.GET['stid'], date, count)
        return HttpResponse(json.dumps(result))
    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def delete_pass(request):
    try:
        ids = request.GET.get('ids', None)
        gid = request.GET.get('gid', None)
        date = request.GET.get('date', None)
        stid = request.GET.get('stid', None)
        errors = []

        if ids:
            passes = Passes.objects.filter(pk__in=json.loads(ids))
            processed = ((p.id, PassLogic.wrap(p).delete()) for p in passes)

            if all([p1[1] for p1 in processed]):
                return HttpResponse(200)

            errors += filter(lambda x: not x[1], processed)

        elif gid and date and stid:
            _pass = Lessons.objects.get(
                group_id=gid,
                student_id=stid,
                date=datetime.datetime.strptime(date, '%d.%m.%Y').date()
            )

            success = PassLogic.wrap(_pass.group_pass).delete()

            return HttpResponse(200) if success else HttpResponseServerError(json.dumps([_pass.id]))

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
        ids = json.loads(request.GET['ids'])
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
        date_from, date_to = (datetime.datetime.strptime(d, '%d.%m.%Y') for d in json.loads(request.GET['date']))
        students = Students.objects.filter(pk__in=ids)
        errors = []

        for student in students:
            try:
                p = Lessons.objects.get(student=student, group=group, date=date_from).group_pass

                # todo пока сделаю так, когда будет менюшка позволяющая снять отметки с занятий, это надо будет убрать.
                # if p.lessons > 0:
                wrapped = PassLogic.wrap(p)
                if not wrapped.freeze(date_from, date_to):
                    errors.append('%s %s' % (student.last_name, student.first_name))

            except Lessons.DoesNotExist:
                errors.append('%s %s' % (student.last_name, student.first_name))

            else:
                pass

        return HttpResponse(200) if not errors else HttpResponseServerError('\n'.join(errors))
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


def delete_debt(group, student, date):
    try:
        debt = Debts.objects.get(group=group, student=student, date=date)
        debt.delete()
        return True

    except Debts.DoesNotExist:
        return False


@auth_decorator
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
        data = json_data.get('checked', [])
        data1 = json_data.get('unchecked', [])
        canceled = json_data.get('canceled', [])

        new_passes = filter(lambda p: isinstance(p, dict), data)
        old_passes = filter(lambda p: isinstance(p, int), data)

        attended_passes = []
        attended_passes_ids = []
        error = []
        now = datetime.datetime.now()

        if not canceled:
            if new_passes:
                for p in new_passes:
                    _pt = int(p['pass_type']) if 'pass_type' in p else None

                    # Списываем с другого абонемента
                    # Списываем с другого абонемента
                    if date <= now and _pt == -1:

                        another_person_pass = Passes.objects.get(pk=p['from_another'])
                        pass_orm_object = Passes(
                            student_id=p['student_id'],
                            group=group,
                            pass_type=another_person_pass.pass_type,
                            start_date=date,
                            lessons=1,
                            skips=0,
                            user=request.user
                        )

                        pass_orm_object.save()
                        wrapped = PassLogic.wrap(pass_orm_object)
                        wrapped.create_lessons(date)

                        another_person_pass.lessons -= 1
                        another_person_pass.save()
                        Lessons.objects.filter(group_pass=another_person_pass).order_by('date').last().delete()
                        attended_passes.append(wrapped)

                    # Проставляем долг
                    elif _pt == -2:
                        if date <= now and not Debts.objects.filter(student_id=p['student_id'], group=group, date=date).exists():
                            debt = Debts(student_id=p['student_id'], group=group, date=date, val=0)
                            debt.save()

                    # Мультикарта
                    elif 'pass_id' in p.iterkeys() and date <= now:
                        pid = p['pass_id']
                        pass_orm_object = Passes.objects.get(pk=pid)

                        if pass_orm_object.lessons == 0:
                            return HttpResponseServerError('no lessons')

                        wrapped = PassLogic.wrap(pass_orm_object)
                        attended_passes.append(wrapped)
                        delete_debt(group, pass_orm_object.student, date)

                    # Любой другой абонемент
                    else:
                        pt = PassTypes.objects.get(pk=_pt)
                        st = Students.objects.get(pk=p['student_id'])
                        lessons_count = p.get('lcnt', None)
                        skips_count = p.get('scnt', None)
                        lessons_exist = map(lambda dt: get_student_lesson_status(st, group, dt)['pass'], group.get_calendar(lessons_count, date))
                        if lessons_count > 1 and any(lessons_exist):
                            error.append(
                                u'%s %s - создаваемый абонемент пересекается с уже созданными абонементами' % (st.last_name, st.first_name)
                            )
                        elif not Passes.objects.filter(student=st, group=group, pass_type=pt, start_date=date).exists():
                            pass_orm_object = Passes(
                                student=st,
                                group=group,
                                pass_type=pt,
                                start_date=date,
                                lessons=lessons_count,
                                skips=skips_count,
                                lessons_origin=lessons_count,
                                skips_origin=skips_count,
                                opener=request.user
                            )
                            pass_orm_object.save()

                            wrapped = PassLogic.wrap(pass_orm_object)
                            wrapped.create_lessons(date, lessons_count)

                            wrapped.presence = p.get('presence', False)
                            if date.date() <= group.last_lesson:
                                attended_passes.append(wrapped)

                            #Убираем долги, если они есть.
                            for _lesson in wrapped.lessons:
                                if delete_debt(group, st, _lesson.date):
                                    _lesson.status = Lessons.STATUSES['attended']
                                    _lesson.save()

                                # map(lambda d: d.delete(), Debts.objects.filter(group=group, student=st, date__range=[wrapped.lessons[0].date, wrapped.lessons[-1].date]))

                    # old
                    if 'debt' in p.iterkeys():
                        if wrapped:
                            lessons = wrapped.lessons
                            debt_val = p['debt']

                            # Создаем и сохраняем долг
                            def new_debt(val, _date):
                                debt = Debts(student_id=p['student_id'], group=group, date=_date, val=val)
                                debt.save()

                            # Если сумма долга больше стоимости абонемента
                            if debt_val >= wrapped.orm_object.pass_type.prise:
                                debt_val /= float(len(lessons))

                                for lesson in lessons:
                                    new_debt(debt_val, lesson.date)

                            # Если долг равен или меньше стоимости абонемента
                            else:

                                for lesson in lessons:
                                    if debt_val > 0:
                                        if debt_val > lesson.prise():
                                            new_debt(lesson.prise(), lesson.date)
                                            debt_val -= lesson.prise()

                                        else:
                                            new_debt(debt_val, lesson.date)
                                            debt_val = 0

            if old_passes and date.date() <= group.last_lesson:
                for pass_orm_object in Passes.objects.select_related().filter(pk__in=old_passes):

                    if pass_orm_object:
                        pass_calendar = Lessons.objects.filter(group_pass=pass_orm_object, date__gte=date).values_list('date', flat=True)

                        if date.date() in pass_calendar:
                            wrapped = PassLogic.wrap(pass_orm_object)
                            wrapped.new_pass = False
                            attended_passes.append(wrapped)

            for _pass in attended_passes:
                if _pass and date <= now:
                    if not _pass.new_pass or _pass.presence:
                        _pass.set_lesson_attended(date, group=group.id)
                    attended_passes_ids.append(_pass.orm_object.id)

            if data1:
                if date.date() <= group.last_lesson:
                    for pass_orm_object in Passes.objects.select_related().filter(pk__in=data1):
                        wrapped = PassLogic.wrap(pass_orm_object)
                        wrapped.set_lesson_not_attended(date)

        else:
            CanceledLessons(group=group, date=date).save()

            for _pass in (PassLogic.wrap(p) for p in Passes.objects.filter(
                    Q(group=group),
                    Q(Q(start_date__lte=date) | Q(frozen_date__lte=date)),
                    Q(lessons__gt=0)
            )):
                if _pass.check_date(date):
                     _pass.cancel_lesson(date)

        if error:
            return HttpResponseServerError(json.dumps(error))

        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


def restore_lesson(request):

    try:
        group = Groups.objects.get(id=request.GET['id'])
        date = datetime.datetime.strptime(request.GET['date'], '%d.%m.%Y')

        for _pass in (PassLogic.wrap(p) for p in Passes.objects.filter(
                    Q(group=group),
                    Q(Q(start_date__lte=date) | Q(frozen_date__lte=date)),
                    Q(lessons__gt=0)
            )):
                if _pass.check_date(date):
                     _pass.restore_lesson(date)

        CanceledLessons.objects.get(group=group, date=date).delete()

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


def write_off_debt(request):
    try:
        debts = Debts.objects.filter(
            student_id=request.GET['sid'],
            group_id=request.GET['gid']
        ).order_by('date')

        val = int(request.GET['val'])

        delta = 0

        for debt in debts:

            if debt.val <= val:
                debt.delete()
                val -= debt.val

            else:
                debt.val -= val
                delta += debt.val
                debt.save()
                val = 0

        return HttpResponse(delta)

    except Exception:
        format_exc()
        return HttpResponseServerError('failed')

@auth_decorator
def create_multipass(request):
    try:
        group = Groups.objects.get(pk=request.GET['group'])
        student = Students.objects.get(pk=request.GET['student'])
        date = datetime.datetime.strptime(request.GET['date'], '%d.%m.%Y')
        ptid = int(request.GET.get('ptid'))

        # if not Passes.objects.filter(student=student, start_date__lte=date, end_date__gte=date).exists():

        pt = PassTypes.objects.get(pk=ptid)
        # pt = PassTypes.objects.get(pk=CLUB_CARD_ID)
        _pass = Passes(
            student=student,
            pass_type=pt,
            start_date=date,
            opener=request.user
        )
        _pass.save()
        PassLogic.wrap(_pass)

        return HttpResponse(200)

    except PassTypes.DoesNotExist:
        return HttpResponseServerError('wrong multypass id, please ste the correct multypass id in the settings file')

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


@auth_decorator
def change_group(request):
    try:
        _json = json.loads(request.GET['data'])
        old_group = Groups.objects.get(pk=int(_json['old_group']))
        new_group = Groups.objects.get(pk=int(_json['new_group']))
        date = datetime.datetime.strptime(_json['date'], '%d.%m.%Y')
        now = datetime.datetime.now().date()
        request_backup = request.GET

        # Собрать информацию по ученику, добавить ее в request и передать на вход add_student
        for student in _json['students']:
            student_orm = Students.objects.get(pk=int(student))
            request.GET = {
                'first_name': student_orm.first_name,
                'last_name': student_orm.last_name,
                'phone': student_orm.phone,
                'id': int(_json['new_group'])
            }

            add_student(request)
            lessons = Lessons.objects.filter(group=old_group, date__gte=date, student=student_orm)
            last_lesson = Lessons.objects.filter(group=new_group, date__gte=date, student=student_orm).order_by('date').last()
            passes = []
            map(lambda x: passes.append(x.group_pass) if x.group_pass not in passes and x.group_pass.one_group_pass else None, lessons)
            calendar = new_group.get_calendar(len(lessons), last_lesson.date + datetime.timedelta(days=1) if last_lesson else date)

            for p in passes:
                pass_lessons = Lessons.objects.filter(group_pass=p, date__gte=date)
                pass_lessons_len = len(pass_lessons)
                if pass_lessons_len > 0:
                    new_pass = Passes(
                        student=p.student,
                        group=new_group,
                        pass_type=p.pass_type,
                        start_date=calendar[0],
                        lessons=pass_lessons_len,
                        skips=p.skips,
                        lessons_origin=pass_lessons.filter(status=Lessons.STATUSES['not_processed']).count(),
                        skips_origin=p.skips_origin,
                        opener=request.user
                    )
                    new_pass.save()

                    wrapped = PassLogic.wrap(new_pass)
                    wrapped.create_lessons(calendar[0], pass_lessons_len)

                    _delete_lessons(p.group.id, p.student.id, calendar[0], pass_lessons_len)

            # if isinstance(add_status, HttpResponseServerError):
            #     return HttpResponseServerError('failed adding')
        # Собрать информацию по передаваемым абонементам, добавить ее в request и передать на вход process_lesson

            request.GET = {
                'group_id': new_group.id,
                'stid': student,
                'msg': u'Переведен из группы: %s - %s c %s' % (old_group.name, '-'.join(old_group.days), date.strftime('%d.%m.%Y'))
            }
            add_or_edit_comment(request)

        request.GET = request_backup
        return HttpResponse(200)

    except Exception:
        print format_exc()
        return HttpResponseServerError('failed')


@auth_decorator
def get_club_card_detail(request):

    try:
        _pass = Passes.objects.get(pk=int(request.GET['pid']))
        student = _pass.student
        result_json = list()
        now = datetime.datetime.now().date()

        def get_lesson(date):
            lesson = get_student_lesson_status(student, group, date)

            # Состояние урока: 1 - доступен для отметки
            #                  0 - отмечен по этому абонементу, не доступен для отметки
            #                  -1 - отмечен по другому абонементу, не доступен для отметки
            if not lesson['attended'] and date.date() <= now:
                lesson['status'] = 1
            elif 'pid' in lesson.iterkeys() and lesson['pid'] == _pass.id:
                lesson['status'] = 0
            else:
                lesson['status'] = -1

            return lesson

        for group in get_student_groups(student, include_closed=True):
            date_from = _pass.start_date if _pass.start_date >= group.start_date else group.start_date
            date_to = group.end_date if group.end_date and group.end_date <= _pass.end_date else _pass.end_date
            days = get_count_of_weekdays_per_interval(group.days, date_from, date_to)
            group_calendar = group.get_calendar(days, date_from)
            lessons_statuses = map(get_lesson, group_calendar)
            lessons = zip(map(lambda d: d.strftime('%d.%m.%Y'), group_calendar), lessons_statuses)

            group_json = {
                'group': {
                    'id': group.id,
                    'name': '%s - %s c %s' % (group.name, ' '.join(group.days), group.time_repr)
                },
                'lessons': lessons
            }

            result_json.append(group_json)

        _json = json.dumps(result_json)
        return HttpResponse(_json)

    except Exception:
        format_exc()
        return HttpResponseServerError('failed')


def add_sampo_payment(request):

    request_body = json.loads(request.GET['data'])
    data = request_body['info']

    date = data.get('date')
    hhmm = data['time']
    if hhmm:
        hhmm = map(int, hhmm.split(':'))
        now = make_aware(datetime.datetime.combine(
            datetime.datetime.strptime(date, '%d.%m.%Y').date() if date else datetime.date.today(),
            datetime.time(hhmm[0], hhmm[1])
        ), timezone(TIME_ZONE))
    else:
        now = make_aware(datetime.datetime.combine(
            datetime.datetime.strptime(date, '%d.%m.%Y').date(),
            datetime.datetime.now().time()
        ), timezone(TIME_ZONE)) if date else datetime.datetime.now(tz=timezone(TIME_ZONE)).replace(second=0, microsecond=0)

    if request.GET['type'].startswith('cash'):
        new_payment = SampoPayments(
            date=now,
            staff=request.user,
            people_count=0,  # Кудрявцев сказал убрать
            money=int(data['count']) * (-1 if request.GET['type'] == 'cash-wrt' else 1)
        )

        comment = data.get('reason')
        if comment:
            new_payment.comment = comment

        new_payment.save()

        passes, payments = get_sampo_details(now)

        return HttpResponse(
            json.dumps({
                'payments': payments
            }))

    elif data and data['name'] and data['surname']:

        new_payment = SampoPayments(
            date=now,
            staff=request.user,
            people_count=1,
            money=1500
        )
        new_payment.save()

        new_pass = SampoPasses(
            name=data['name'],
            surname=data['surname'],
            payment=new_payment
        )
        new_pass.save()

        passes, payments = get_sampo_details(now)

        return HttpResponse(
            json.dumps({
                'pid': new_pass.id,
                'payments': payments
            }))

    else:
        return HttpResponseServerError('Not all variables')


def check_uncheck_sampo(request):

    action = request.GET.get('action')
    hhmm = map(lambda x: int(x), request.GET['time'].split(':'))
    date_str = request.GET.get('date')

    if date_str:
        date = map(lambda x: int(x), date_str.split('.'))
        date_params = dict(
            zip(('day', 'month', 'year', 'hour', 'minute'), date+hhmm)
        )
        date_params['tz'] = timezone(TIME_ZONE)
        now = datetime.datetime(**date_params)
    else:
        now = datetime.datetime.now(tz=timezone(TIME_ZONE)).replace(hour=hhmm[0], minute=hhmm[1], second=0, microsecond=0)

    if action == 'check':
        new_usage = SampoPassUsage(
            sampo_pass_id=int(request.GET['pid']),
            date=now
        )

        new_usage.save()

        passes, payments = get_sampo_details(now)

        _json = json.dumps({
            'payments': payments
        })

        return HttpResponse(_json)

    elif action == 'uncheck':
        # todo Если админ системы удалит запись отсюда за любой день кроме сегоднешнего, удалится не та запись!
        # todo решать эту проблему лучше через передачу в функцию праильной даты...
        last_usage = SampoPassUsage.objects.filter(
            sampo_pass_id=int(request.GET['pid']),
            date__range=(
                now.replace(hour=0, minute=0, second=0, microsecond=0),
                now.replace(hour=23, minute=59, second=59, microsecond=999999)
            )
        ).last()

        if last_usage:
            last_usage.delete()

        passes, payments = get_sampo_details(now)

        _json = json.dumps({
            'payments': payments
        })

        return HttpResponse(_json)

    else:
        return HttpResponseServerError('failed')


def write_off_sampo_record(request):

    u"""
    Функция для удаления записи о посещении сампо
    :param request:
    :return:
    """

    pid = request.GET.get('pid')

    if not pid:
        return HttpResponseServerError('No record id')

    if pid.startswith('p'):
        to_delete, pass_to_delete = None, None

        try:
            to_delete = SampoPayments.objects.get(pk=int(pid[1:]))
            msg = '%s удалил(а) запись из таблицы "Оплаты наличными": | %s |' % (request.user, to_delete)

            try:
                pass_to_delete = SampoPasses.objects.get(payment=to_delete)
                SampoPassUsage.objects.filter(sampo_pass=pass_to_delete).delete()
                pass_to_delete.delete()
                msg = u'%s удалил(а) запись из таблицы "Абонементы на сампо": | %s |' % (request.user, pass_to_delete)

            except SampoPasses.DoesNotExist:
                pass

            to_delete.delete()
            write_log(msg)

        except SampoPassUsage.DoesNotExist:
            pass

    date_str = request.GET.get('date')

    date = make_aware(datetime.datetime.strptime(date_str, '%d.%m.%Y'), timezone(TIME_ZONE)) if date_str else datetime.datetime.now(timezone(TIME_ZONE))
    date_min = datetime.datetime.combine(date.date(), datetime.datetime.min.time())
    date_max = datetime.datetime.combine(date.date(), datetime.datetime.max.time())

    response = dict()
    passes, payments = get_sampo_details(date_max)
    usages = SampoPassUsage.objects.filter(
        date__range=[date_min, date_max]
    ).values_list('sampo_pass', flat=True)

    def to_json(elem):
        _json = elem.__json__()
        _json['usage'] = long(elem.id) in usages
        return _json

    response['passes'] = map(to_json, passes)
    response['payments'] = payments

    return HttpResponse(json.dumps(response))
