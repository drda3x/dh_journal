# -*- coding:utf-8 -*-
import datetime
import re
from pytz import timezone, UTC
from project.settings import TIME_ZONE
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseServerError
from auth import check_auth, log_out
from django.template import RequestContext
from django.template.context_processors import csrf

from application.utils.passes import get_color_classes
from application.utils.groups import get_groups_list, get_group_detail, get_student_lesson_status, get_group_students_list
from application.utils.date_api import get_month_offset, get_last_day_of_month, MONTH_RUS
from application.models import Lessons, User, Passes
from application.auth import auth_decorator
from application.utils.date_api import get_count_of_weekdays_per_interval
from application.utils.sampo import get_sampo_details

from models import Groups, Students, User, PassTypes, BonusClasses, BonusClassList


def custom_proc(request):
    "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'My app',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def prev_cur(arr):
    itr = iter(arr[:])
    prev = None

    try:
        prev = itr.next()
    except StopIteration:
        yield None

    for elem in itr:
        yield prev, elem
        prev = elem


def index_view(request):

    user = check_auth(request)
    main_template = 'main_view.html'
    login_template = 'login.html'

    if user:

        context = dict()
        context['user'] = user

        if user.teacher:

            context['groups'] = get_groups_list(user)
            context['now'] = datetime.datetime.now().date()

            other_groups = context['groups'].get('other')

            if other_groups:
                other_groups.sort(key=lambda e: e['name'].replace('[\s-]', '').lower())

                try:
                    for prev, cur in prev_cur(other_groups):
                        if re.sub(r'[\s-]', '', prev['name']).lower() != re.sub(r'[\s-]', '', cur['name']).lower():
                            other_groups.insert(other_groups.index(cur), {'name': 'divider'})
                except TypeError:
                    pass

        elif user.sampo_admin:
            return sampo_view(request)

        return render_to_response(main_template, context, context_instance=RequestContext(request, processors=[custom_proc]))

    else:
        args = {}
        args.update(csrf(request))
        return render_to_response(login_template, args, context_instance=RequestContext(request, processors=[custom_proc]))


def user_log_out(request):
    log_out(request)
    return redirect('/')


@auth_decorator
def group_detail_view(request):

    context = {}
    template = 'group_detail.html'
    date_format = '%d%m%Y'

    try:
        group_id = int(request.GET['id'])
        now = datetime.datetime.now()
        group = Groups.objects.get(pk=group_id)

        if 'date' in request.GET:
            date_from = datetime.datetime.strptime(request.GET['date'], date_format)

        elif group.end_date and not group.is_opened:
            date_from = datetime.datetime.combine(group.end_date, datetime.datetime.min.time()).replace(day=1)

        else:
            date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if date_from.date() < group.start_date:
            date_from = datetime.datetime.combine(group.start_date, datetime.datetime.min.time())

        try:
            last_lesson = datetime.datetime.combine(
                Lessons.objects.filter(group=group).latest('date').date,
                datetime.datetime.min.time()
            )

        except Lessons.DoesNotExist:
            last_lesson = None

        date_to = group.end_datetime or get_last_day_of_month(date_from)

        forward_month = max(
            get_last_day_of_month(now) + datetime.timedelta(days=1 if not group.end_datetime else 0),
            last_lesson.replace(day=1)
        ) if last_lesson else get_last_day_of_month(now) + datetime.timedelta(days=1 if not group.end_datetime else 0)

        border = datetime.datetime.combine(group.start_date, datetime.datetime.min.time()).replace(day=1)

        context['control_data'] = {
            'constant': {
                'current_date_str': '%s %d' % (MONTH_RUS[date_from.month], date_from.year),
                'current_date_numval': date_from.strftime(date_format)
            },
            'date_control': map(
                lambda d: {'name': '%s %d' % (MONTH_RUS[d.month], d.year), 'val': d.strftime(date_format)},
                filter(
                    lambda x1: x1 >= border,
                    map(lambda x: get_month_offset(forward_month.date(), x), xrange(0, 8))
                )
            )
        }
        context['single_pass_id'] = PassTypes.objects.filter(name__iregex='Разовое занятие').values('id')

        html_color_classes = {
            key: val for val, key in get_color_classes()
        }

        context['passes_color_classes'] = [
            {'name': val, 'val': key} for key, val in html_color_classes.iteritems()
        ]

        context['group_detail'] = get_group_detail(group_id, date_from, date_to)
        context['pass_detail'] = PassTypes.objects.filter(one_group_pass=True, pk__in=group.available_passes).order_by('sequence').values()
        context['other_groups'] = Groups.objects.exclude(id=group.id).exclude(is_opened=False)

        for elem in context['pass_detail']:
            elem['skips'] = '' if elem['skips'] is None else elem['skips']

        for det in context['pass_detail']:
            det['html_color_class'] = html_color_classes[det['color']]

        context['error'] = False

    except Groups.DoesNotExist:

        context['error'] = True

    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))


def user_profile_view(request):
    template = 'user_profile.html'
    uid = request.GET['uid']
    context = {
        'user': User.objects.get(pk=uid)
    }

    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))


def print_view(request):

    router = {
        'full': print_full,
        'lesson': print_lesson
    }

    return router[request.GET['type']](request)


def print_full(request):
    context = {}
    date_format = '%d%m%Y'
    template = 'print_full.html'
    group_id = request.GET['id']
    date = request.GET.get('date', None)

    date_from = datetime.datetime.strptime(request.GET['date'], date_format) if date\
        else datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    date_to = get_last_day_of_month(date_from)
    html_color_classes = {
        key: val for val, key in get_color_classes()
    }

    context['passes_color_classes'] = [
        {'name': val, 'val': key} for key, val in html_color_classes.iteritems()
    ]
    context['date_str'] = '%s %d' % (MONTH_RUS[date_from.month], date_from.year)
    context['group_detail'] = get_group_detail(group_id, date_from, date_to, date_format='%d.%m.%y')

    context['subtype'] = request.GET.get('subtype', None)

    if not context['subtype']:
        raise TypeError('wrong subtype')

    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))


def print_lesson(request):
    context = {}
    template = 'print_lesson.html'
    date_format = '%d%m%Y'

    date = datetime.datetime.strptime(request.GET['date'], date_format).date()
    group = Groups.objects.get(pk=request.GET['id'])
    html_color_classes = {
        key: val for val, key in get_color_classes()
    }
    context['passes_color_classes'] = [
            {'name': val, 'val': key} for key, val in html_color_classes.iteritems()
        ]
    context['group_name'] = group.name
    context['date'] = date.strftime('%d.%m.%Y')
    context['students'] = map(lambda s: dict(data=get_student_lesson_status(s, group, date), info=s), get_group_students_list(group))

    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))


@auth_decorator
def club_cards(request):
    context = {}
    template = 'club_cards.html'
    date_format = '%d%m%Y'

    user = request.user
    now = datetime.datetime.now()
    date_from = datetime.datetime.strptime(request.GET['date'], date_format) if 'date' in request.GET\
        else now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    date_to = get_last_day_of_month(date_from)

    last_pass = Passes.objects.filter(pass_type__one_group_pass=0).order_by('end_date').last()
    down_border = (now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)).replace(day=1)

    context['control_data'] = {
        'constant': {
            'current_date_str': '%s %d' % (MONTH_RUS[date_from.month], date_from.year),
            'current_date_numval': date_from.strftime(date_format)
        },
        'date_control': map(
            lambda d: {'name': '%s %d' % (MONTH_RUS[d.month], d.year), 'val': d.strftime(date_format)},
            filter(
                lambda x: x >= down_border,
                map(lambda x: get_month_offset(last_pass.end_date if last_pass else date_from, x), xrange(0, 8))
            )
        )
    }

    first_day_of_month = datetime.datetime(date_from.year, date_from.month, 1)
    all_passes = Passes.objects\
        .filter(pass_type__one_group_pass=0, start_date__lte=date_to, end_date__gte=date_from)\
        .select_related('student').order_by('student__last_name', 'student__first_name')\
        .order_by('-start_date')
    for _p in all_passes:
        _p.prev_month = len(_p.get_lessons_before_date(first_day_of_month))
        _p.money = _p.lessons * _p.one_lesson_prise

    ordered = all_passes.order_by('start_date')
    borders = (ordered.first(), ordered.last())
    groups = get_groups_list(user)
    date_group_list = {}

    all_groups = groups['self'] + (groups['other'] if 'other' in groups.iterkeys() else [])

    if borders[0] and borders[1]:
        for group in all_groups:
            days = group['days'].split(' ')
            count = get_count_of_weekdays_per_interval(days, borders[0].start_date, borders[1].end_date)
            calendar = filter(lambda d1: d1.date() >= group['orm'].start_date, group['orm'].get_calendar(count, borders[0].start_date))

            for p in all_passes:
                for d in filter(lambda x: p.start_date <= x.date() <= p.end_date and x <= now, calendar):
                    if d not in date_group_list.iterkeys():
                        date_group_list[d] = []

                    date_group_list[d].append('g%dp%d' % (group['id'], p.id))

    for group in all_groups:
        group['students'] = ' s'.join(
            [
                str(s.id)
                for s in filter(
                    lambda st: st in [p.student for p in all_passes],
                    get_group_students_list(group['id'])
                )
            ]
        )

        group['students'] = ('s' if group['students'] else '') + group['students']

    students = [{'id': x['id'], 'list': get_group_students_list(x['id'])} for x in all_groups]

    context['date_list'] = map(
        lambda x: {'key': x, 'label': x.strftime('%d.%m.%Y'), 'val': ' '.join(date_group_list[x])},
        date_group_list
    )
    context['expire'] = (now - datetime.timedelta(days=14)).date()
    context['now'] = now.date()
    context['user'] = user
    context['date_list'].sort(key=lambda x: x['key'])
    context['groups'] = groups
    context['passes'] = all_passes
    context['pass_types'] = PassTypes.objects.filter(one_group_pass=0)
    context['students'] = students

    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))


@auth_decorator
def history_view(request):

    template = 'history.html'
    border = datetime.datetime.now().date() - datetime.timedelta(days=90)
    border.replace(day=1)
    groups = get_groups_list(request.user, False)
    context = {
        'groups': filter(lambda g: not g['orm'].end_date or g['orm'].end_date >= border, groups['self'] + (groups['other'] if 'other' in groups.iterkeys() else [])),
        'user': request.user
    }

    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))


@auth_decorator
def sampo_view(request):

    from application.api import add_sampo_payment, check_uncheck_sampo, write_off_sampo_record

    actions = {
        'add': add_sampo_payment,
        'check': check_uncheck_sampo,
        'uncheck': check_uncheck_sampo,
        'del': write_off_sampo_record
    }

    action = request.GET.get('action')

    if action:
        return actions[action](request)

    date_str = request.GET.get('date')

    try:
        date = datetime.datetime.strptime('%s 23:59:59' % date_str, '%d.%m.%Y %H:%M:%S') if date_str else datetime.datetime.now()

    except Exception:
        return HttpResponseServerError('Не правильно указана дата')

    context = dict()
    context['passes'], context['today_payments'], context['totals'] = get_sampo_details(date)
    context['pass_signs'] = filter(lambda x: not x['info']['type'], context['today_payments'])
    context['pass_signs_l'] = len(context['pass_signs'])
    context['date'] = date.strftime('%d.%m.%Y')
    template = 'main_view.html' if not request.user.teacher else 'sampo_full.html'
    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))


@auth_decorator
def bonus_class_view(request):

    from application.api import mk_add_student, mk_remove_student, mk_attendance

    bonus_class_handlers = {
        'addStudent': mk_add_student,
        'removeStudent': mk_remove_student,
        'setAttendance': mk_attendance
    }

    try:
        return bonus_class_handlers[request.GET.get('requestType')](request)
    except KeyError:
        pass

    mkid = request.GET.get('id')

    template = 'mk.html'

    context = dict()
    context['group_id'] = mkid
    context['students'] = BonusClassList.objects.select_related().filter(group__id=mkid)

    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))