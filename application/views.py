# -*- coding:utf-8 -*-
import datetime
import re
import json
from django.contrib import auth
from django.views.generic import TemplateView
from django.contrib.sessions.backends.db import SessionStore
from pytz import timezone, UTC
from project.settings import TIME_ZONE
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseServerError, HttpResponse
from auth import check_auth, log_out
from django.template import RequestContext
from django.template.context_processors import csrf
from django.utils.timezone import make_aware
from django.db.models import Sum, Q, Max, Count
from django.utils.functional import cached_property

from application.logic.student import add_student as _add_student, remove_student as _remove_student, edit_student as _edit_student
from application.logic.group import GroupLogic

from application.utils.passes import get_color_classes, PassLogic, ORG_PASS_HTML_CLASS
from application.utils.groups import get_groups_list, get_group_detail, get_student_lesson_status, get_group_students_list, get_student_groups
from application.utils.date_api import get_month_offset, get_last_day_of_month, MONTH_RUS
from application.models import (
    Lessons,
    User,
    Passes,
    GroupList,
    SampoPayments,
    SampoPasses,
    SampoPassUsage,
    Debts,
    GroupLevels,
    TeachersSubstitution,
    AdminCalls,
    CanceledLessons,
    AdministratorList
)
from application.auth import auth_decorator
from application.utils.date_api import get_count_of_weekdays_per_interval
from application.utils.sampo import get_sampo_details, write_log

from models import Groups, Students, User, PassTypes, BonusClasses, BonusClassList, Comments # todo ненужный импорт
from collections import namedtuple, defaultdict, Counter
from itertools import groupby, takewhile
from application.utils.phones import check_phone
import traceback


def custom_proc(request):
    "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'My app',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def delete_debt(group, student, date):

    params = dict(date=date)

    if isinstance(student, int):
        params['student_id'] = student
    else:
        params['student'] = student

    if isinstance(group, int):
        params['group_id'] = group
    else:
        params['group'] = group

    try:
        debt = Debts.objects.get(**params)
        debt.delete()
        return True

    except Debts.DoesNotExist:
        return False

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
        context['single_pass_id'] = PassTypes.all.filter(name__iregex='Разовое занятие').values('id')

        html_color_classes = {
            key: val for val, key in get_color_classes()
        }

        context['passes_color_classes'] = [
            {'name': val, 'val': key} for key, val in html_color_classes.iteritems()
        ]

        context['group_detail'] = get_group_detail(group_id, date_from, date_to)
        context['pass_detail'] = json.dumps([
            p.__json__()
            for p in PassTypes.all.filter(pk__in=group.available_passes).order_by('sequence').values()
        ])
        context['other_groups'] = Groups.opened.exclude(id=group.id)

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


# С этого момента начинается эра нормального кода!!!
# Теперь я буду потехоньку переписывать все на классы.
# А когда-нибудь у меня будет нормальная структура всего проекта!!!
# УРА ТОВАРИЩИ!!!


def request_handler(func):
    def handler(self, *args, **kwargs):
        try:
            request = args[-1]
            data = json.loads(request.POST['data'])
            resp = func(self, **data)

            return HttpResponse(resp or 200)
        except Exception:
            traceback.format_exc()
            return HttpResponseServerError()

    return handler


class BaseView(TemplateView):
    """
    Базовый класс для всех вьюшек
    проверяет авторизацию и если надо выбрасывает на страницу авторизации
    """

    abstract = True

    def get_authenticated_user(self, request):

        try:
            user = User.objects.get(pk=request.session.get('uid'))
        except User.DoesNotExist:
            user = None

        if user and user.is_authenticated():
            return user
        else:
            return None

    def dispatch(self, request, *args, **kwargs):
        user = self.get_authenticated_user(request)

        if user:
            self.request = request
            self.request.user = user
            return super(BaseView, self).dispatch(request, *args, **kwargs)

        else:
            return redirect('/login')

    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)

        return context

    def post(self, *args, **kwargs):
        action_name = self.request.POST.get('action')

        if action_name:
            try:
                return getattr(self, action_name)(*args, **kwargs)

            except Exception:
                traceback.format_exc()
                return HttpResponseServerError()

        else:
            return HttpResponseServerError('wrong action name')



class IndexView(BaseView):
    template_name = 'base.html'

    class Url(dict):
        """
        Класс для создания обыкновенных ссылок на странице
        """
        def __init__(self, *args, **kwargs):

            if len(args) == 1:
                if isinstance(args[0], Groups):
                    group_repr = args[0].__json__()
                    self.update(group_repr)

                    if kwargs.get('is_superuser', False):
                        profit = GroupLogic(args[0]).profit()
                        self['profit'] = profit[0][1] if profit else None

                    #self['label'] = '%s %s %s %s' % (
                    #    group_repr['dance_hall']['station'],
                    #    group_repr['days'],
                    #    group_repr['time'],
                    #    group_repr['name']
                    #)

                    self['url'] = 'group/%d' % group_repr['id']

            else:
                self['label'], self['url'] = args

    def get(self, *args, **kwargs):
        user = self.request.user

        #Если пользователь - админ сампо, отправляем его на другую вьюшку
        if user.teacher or user.id == 28:
            return super(IndexView, self).get(self.request, *args, **kwargs)

        elif user.sampo_admin:
            return redirect('/sampo')

        else:
            # Всех остальных - лесом!
            return HttpResponseServerError(403)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        now = datetime.datetime.now()
        context['now'] = now.date()

        depth = 1
        menu = []
        user = self.request.user
        month_start = datetime.datetime.strptime('01.%d.%d' % (now.month, now.year), '%d.%m.%Y')

        substitutions_qs = TeachersSubstitution.objects.filter(
            teachers=user,
            date__range= [
                datetime.datetime.strptime('01.%d.%d' % (now.month, now.year), '%d.%m.%Y'),
                datetime.datetime.strptime('28.%d.%d' % (now.month, now.year), '%d.%m.%Y') + datetime.timedelta(weeks=2)
            ]
        ).values_list('group_id', flat=True)

        # Меню для руководства
        if user.is_superuser:
            groups = Groups.opened

            # Мои группы
            menu.append({
                'label':u'Мои группы',
                'depth': str(depth),
                'hideable': False,
                'urls': [
                    self.Url(g, is_superuser=True) for g in groups.filter(teachers=user)
                ]
            })

            depth += 1
            menu.append({
                'label': u'Замены',
                'depth': str(depth),
                'hideable': True,
                'urls': [
                    self.Url(g, is_superuser=True) for g in  groups.filter(pk__in=substitutions_qs).exclude(teachers=user)
                ]
            })

            # Группы других преподавателей
            depth += 1
            menu.append({
                'label': u'Остальные группы',
                'depth': str(depth),
                'hideable': False,
                'type': 'urls',
                'urls': [
                    {
                        'label': level.name,
                        'hideable': True,
                        'depth': '%d_%d' % (depth, level_depth),
                        'type': 'urls',
                        'urls': [
                            self.Url(g, is_superuser=True) for g in groups.filter(level=level).exclude(teachers=user)
                        ]
                    } for level_depth, level in enumerate(GroupLevels.objects.all())
                ]
            })

            #Мастер-классы
            #depth += 1
            #menu.append({
            #    'label': u'Мастер-классы',
            #    'depth': str(depth),
            #    'hideable': True,
            #    'url_pattern': 'mk',
            #    'type': 'header',
            #    'urls': [b.__json__() for b in BonusClasses.objects.select_related().filter(date__gte=context['now']).order_by('-date')] + [self.Url(u'-- все прошедшие классы', 'bkhistory').__json__()]
            #})

            #Закрытые группы
            depth += 1
            menu.append({
                'label': u'Закрытые группы',
                'depth': str(depth),
                'hideable': True,
                'type': 'groups',
                'urls': [self.Url(g, is_superuser=True) for g in Groups.closed.all().order_by('-end_date')[:5]] + [self.Url(u'--все закрытые группы--', 'history')]
            })

            depth += 1
            menu.append({
                'label': u'Отчеты',
                'depth': str(depth),
                'hideable': False,
                'type': 'urls',
                'urls': [self.Url(u'Финансовый отчет', 'finance'), self.Url(u'Помойка', 'adminlist')]
            })

        # Меню для других преподов
        else:
            # Мои группы
            menu.append({
                'label': u'Группы',
                'depth': str(depth),
                'hideable': False,
                'type': 'groups',
                'urls': [
                    self.Url(g) for g in Groups.opened.filter(teachers=user)
                ]
            })

            depth += 1
            menu.append({
                'label': u'Замены',
                'depth': str(depth),
                'hideable': True,
                'type': 'groups',
                'urls': [
                    self.Url(g) for g in Groups.objects.filter(pk__in=substitutions_qs).exclude(teachers=user)
                ]
            })

            #Мастер-классы
            #depth += 1
            #menu.append({
            #    'label': u'Мастер-классы',
            #    'depth': str(depth),
            #    'hideable': True,
            #    'type': 'groups',
            #    'urls': [b.__json__() for b in BonusClasses.objects.select_related().filter(teachers=user).order_by('-date')]
            #})

            #Закрытые группы
            depth += 1
            menu.append({
                'label': u'Закрытые группы',
                'depth': str(depth),
                'hideable': True,
                'type': 'groups',
                'urls': [self.Url(g) for g in Groups.closed.filter(teachers=user).order_by('-end_date')[:5]] + [self.Url(u'--все закрытые группы--', 'history')]
            })

        #Общеклубное меню
        depth += 1
        menu.append({
            'label': u'Клуб',
            'depth': str(depth),
            'hideable': False,
            'type': 'urls',
            'urls': [self.Url(u'Клубные карты', 'clubcards'), self.Url(u'САМПО', 'sampo')]
        })

        context['menu'] = json.dumps(menu)

        #TODO надо проверить, что с доменом тоже будет работать
        context['host'] = self.request.get_host()

        return context


class LoginView(TemplateView):
    u"""
    Вьюшка для работы с авторизацией
    """

    template_name = 'login.html'

    def login(self, username, password, remember=False):
        user = auth.authenticate(username=username, password=password)

        if user and user.is_active:
            if remember:
                auth.login(self.request, user)

            session = SessionStore()
            session['uid'] = user.id

            return session

        else:
            return None

    def get_context_data(self, status_code=200, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['login_failed'] = status_code != 200

        return context

    def post(self, request, *args, **kwargs):
        username = request.POST['username'] if 'username' in request.POST else None
        password = request.POST['password'] if 'password' in request.POST else None
        remember = 'remember' in request.POST

        request.session = self.login(username, password, remember)
        if request.session:
            return redirect('/')

        else:
            context = self.get_context_data(403)
            return self.render_to_response(context)


def user_log_out(request):
    request.session.delete()
    auth.logout(request)

    return redirect('/')


class SampoView(BaseView):
    """
    Вьюшка для работы с САМПО
    """

    template_name = 'sampo_full.html'

    # Исходники для функций ниже
    # from application.api import add_sampo_payment, check_uncheck_sampo, write_off_sampo_record
    def add_sampo_payment(self):
        request_body = json.loads(self.request.GET['data'])
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

        if self.request.GET['type'].startswith('cash'):
            new_payment = SampoPayments(
                date=now,
                staff=self.request.user,
                people_count=0,  # Кудрявцев сказал убрать
                money=int(data['count']) * (-1 if self.request.GET['type'] == 'cash-wrt' else 1)
            )

            comment = data.get('reason')
            if comment:
                new_payment.comment = comment

            new_payment.save()

            passes, payments, _ = get_sampo_details(now)

            return HttpResponse(
                json.dumps({
                    'payments': payments
                }))

        elif data and data['name'] and data['surname']:

            new_payment = SampoPayments(
                date=now,
                staff=self.request.user,
                people_count=1,
                money=int(data['count'] or 0)
            )
            new_payment.save()

            new_pass = SampoPasses(
                name=data['name'],
                surname=data['surname'],
                payment=new_payment
            )
            new_pass.save()

            passes, payments, _ = get_sampo_details(now)

            return HttpResponse(
                json.dumps({
                    'pid': new_pass.id,
                    'payments': payments
                }))

        else:
            return HttpResponseServerError('Not all variables')

    def check_uncheck_sampo(self):
        action = self.request.GET.get('action')
        time = self.request.GET.get('time')

        if time:
            hhmm = map(lambda x: int(x), self.request.GET['time'].split(':'))
        else:
            hhmm = [0, 0]

        date_str = self.request.GET.get('date')

        if date_str:
            date = map(lambda x: int(x), date_str.split('.'))
            date_params = dict(
                zip(('day', 'month', 'year', 'hour', 'minute'), date+hhmm)
            )
            now = make_aware(datetime.datetime(**date_params), timezone(TIME_ZONE))
        else:
            now = make_aware(datetime.datetime.now(), timezone(TIME_ZONE)).replace(hour=hhmm[0], minute=hhmm[1], second=0, microsecond=0)

        if action == 'check':
            new_usage = SampoPassUsage(
                sampo_pass_id=int(self.request.GET['pid']),
                date=now
            )

            new_usage.save()

            passes, payments, _ = get_sampo_details(now)

            _json = json.dumps({
                'payments': payments
            })

            return HttpResponse(_json)

        elif action == 'uncheck':
            # todo Если админ системы удалит запись отсюда за любой день кроме сегоднешнего, удалится не та запись!
            # todo решать эту проблему лучше через передачу в функцию праильной даты...
            last_usage = SampoPassUsage.objects.filter(
                sampo_pass_id=int(self.request.GET['pid']),
                date__range=(
                    now.replace(hour=0, minute=0, second=0, microsecond=0),
                    now.replace(hour=23, minute=59, second=59, microsecond=999999)
                )
            ).last()

            if last_usage:
                last_usage.delete()

            passes, payments, _ = get_sampo_details(now)

            _json = json.dumps({
                'payments': payments
            })

            return HttpResponse(_json)

        else:
            return HttpResponseServerError('failed')

    def write_off_sampo_record(self):
        pid = self.request.GET.get('pid')

        if not pid:
            return HttpResponseServerError('No record id')

        if pid.startswith('p'):
            to_delete, pass_to_delete = None, None

            try:
                to_delete = SampoPayments.objects.get(pk=int(pid[1:]))
                msg = '%s удалил(а) запись из таблицы "Оплаты наличными": | %s |' % (self.request.user, to_delete)

                try:
                    pass_to_delete = SampoPasses.objects.get(payment=to_delete)
                    SampoPassUsage.objects.filter(sampo_pass=pass_to_delete).delete()
                    pass_to_delete.delete()
                    msg = u'%s удалил(а) запись из таблицы "Абонементы на сампо": | %s |' % (self.request.user, pass_to_delete)

                except SampoPasses.DoesNotExist:
                    pass

                to_delete.delete()
                write_log(msg)

            except SampoPassUsage.DoesNotExist:
                pass

        date_str = self.request.GET.get('date')

        date = make_aware(datetime.datetime.strptime(date_str, '%d.%m.%Y'), timezone(TIME_ZONE)) if date_str else datetime.datetime.now(timezone(TIME_ZONE))
        date_min = datetime.datetime.combine(date.date(), datetime.datetime.min.time())
        date_max = datetime.datetime.combine(date.date(), datetime.datetime.max.time())

        response = dict()
        passes, payments, _ = get_sampo_details(date_max)
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

    def get(self, request, *args, **kwargs):
        actions = {
            'add': self.add_sampo_payment,
            'check': self.check_uncheck_sampo,
            'uncheck': self.check_uncheck_sampo,
            'del': self.write_off_sampo_record
        }

        action = request.GET.get('action')

        if action:
            return actions[action]()

        else:
            context = self.get_context_data(*args, **kwargs)

            if not self.request.user.teacher:
                self.template_name = 'main_view.html'

            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SampoView, self).get_context_data(**kwargs)

        date_str = self.request.GET.get('date')

        try:
            if date_str:
                date = datetime.datetime.strptime(
                    '%s 23:59:59' % date_str, '%d.%m.%Y %H:%M:%S'
                )
            else:
                date = datetime.datetime.now()

        except Exception:
            return HttpResponseServerError('Не правильно указана дата')

        context['passes'], context['today_payments'], context['totals'] = get_sampo_details(date)
        context['pass_signs'] = filter(lambda x: not x['info']['type'], context['today_payments'])
        context['pass_signs_l'] = len(context['pass_signs'])
        context['date'] = date.strftime('%d.%m.%Y')
        context['report'] = self.get_report(date)

        return context

    def get_report(self, _date):

        date = _date.replace(day=1)
        month_num = date.month
        day = datetime.timedelta(days=1)
        today = datetime.date.today()
        report = []
        Record = namedtuple(
            "Record",
            ['date', 'incomming', 'passes', 'classes', 'outgoing', 'total']
        )

        total_saldo = 0

        while date.month == month_num:
            payments = SampoPayments.objects.filter(date__range=[
                datetime.datetime.combine(date, datetime.datetime.min.time()).replace(tzinfo=UTC),
                datetime.datetime.combine(date, datetime.datetime.max.time()).replace(tzinfo=UTC)
            ])

            passes = SampoPasses.objects \
                .select_related('payment') \
                .filter(payment__in=payments)

            incoming = payments.filter(money__gte=0).aggregate(
                total=Sum("money")
            )

            passes = passes.aggregate(
                total=Sum("payment__money")
            )

            #outgoing = payments.filter(money__lte=0).aggregate(
            #    total=Sum("money")
            #    )

            outgoing = payments.filter(money__lt=0)

            total = payments.aggregate(total=Sum("money"))
            total_saldo += total['total'] or 0

            report.append(
                Record(
                    date.day,
                    incoming['total'] or '-',
                    passes['total'] or '-',
                    ((incoming['total'] or 0) - (passes['total'] or 0)) or '-',
                    # abs(outgoing['total'] or 0) or '-',
                    outgoing,
                    total_saldo if today >= date.date() else '-'
                )
            )

            date += day

        return report


class BonusClassView(BaseView):
    """
    Вьюшка для работы с мастер-классами
    """

    template_name = 'mk.html'

    def add(self, request):

        if request.POST.get('id'):
            _json = _edit_student(
                request.POST['id'],
                request.POST['phone'],
                request.POST['first_name'],
                request.POST['last_name'],
                request.POSTget('e_mail'),
                request.POST.get('is_org')
            )

        else:
            _json = _add_student(
                request.POST['gid'],
                (request.POST['first_name'], request.POST['last_name'], request.POST['phone']),
                request.POST.get('e_mail'),
                request.POST.get('is_org'),
                BonusClassList
            )

        return HttpResponse(json.dumps(_json)) if _json else HttpResponseServerError('failed')

    def delete(self, request):
        try:
            ids = json.loads(request.POST['ids'])
            gid = request.POST['gid']

            if _remove_student(gid, ids, BonusClassList):
                return HttpResponse(200)
            else:
                return HttpResponseServerError('failed')

        except Exception:
            from traceback import format_exc
            print(format_exc())

            return HttpResponseServerError()

    def attendance(self, request):
        gid = request.POST['gid']
        student_id = request.POST['stid']
        val = request.POST.get('val') == u'true'

        BonusClassList.objects.get(group_id=gid, student_id=student_id).update(attendance=val)

        return HttpResponse(200)

    def add_pass(self, request):
        gid = int(request.POST['gid'])
        mkid = int(request.POST['mkid'])

        mk = BonusClasses.objects.get(pk=mkid)
        group = Groups.objects.get(pk=gid)
        student = Students.objects.get(pk=int(request.POST['stid']))
        pass_type = PassTypes.all.get(pk=int(request.POST['ptid']))

        _add_student(gid, student, group_list_orm=GroupList)

        _pass = Passes(
            student=student,
            group=group,
            pass_type=pass_type,
            bonus_class_id=mkid
        )
        _pass.save()

        if mk.within_group and mk.within_group.id == gid \
                and not Lessons.objects.filter(group=group, student=student, date=mk.date).exists():
            one_time_pass = Passes(
                student=student,
                group=group,
                pass_type_id=44,
                bonus_class_id=mkid,
                start_date=mk.date
            )
            one_time_pass.save()

            _p = PassLogic.wrap(one_time_pass)
            _p.create_lessons(mk.date)
            _p.process_lesson(mk.date, Lessons.STATUSES['attended'])

        # Создаем фантомный абонемент, который, до того как по нему пошли отметки, будет каждый раз начинаться с последнего занятия!!!

        # Если у этого студента, в эту группу есть абонемент и этот абонемент еще не закончен, то новый абонемент
        # надо впихивать после него, а если абонемента нет или он уже кончился, то новый впихиваем на следующее занятие...
        BonusClassList.objects.get(group_id=mkid, student=student).update(attendance=True)

        return HttpResponse(200, json)

    def delete_pass(self, request):
        mkid = int(request.POST['gid'])
        stid = int(request.POST['stid'])
        passes = Passes.objects.filter(bonus_class_id=mkid, student_id=stid)

        for p in passes:
            if not Lessons.objects.filter(student_id=stid, group=p.group).exists():
                try:
                    GroupList.objects.get(group=p.group, student_id=stid).delete()

                except GroupList.DoesNotExist:
                    pass

            p.delete()

        return HttpResponse(200)

        #else:
        #    return HttpResponseServerError('По данному абонементу были произведены отметки в группе')

    @staticmethod
    def save_comment(request):
        try:
            cid = request.POST.get('cid')
            if cid:
                comment = Comments.objects.get(pk=cid)
                comment.text = request.POST.get('text')
                comment.save()
            else:
                comment = Comments(
                    student_id=request.POST['stid'],
                    bonus_class_id=request.POST['group'],
                    text=request.POST.get('text'),
                    add_date=datetime.datetime.now()
                )
                comment.save()

            return HttpResponse(json.dumps({'id': comment.id}))

        except Exception:
            from traceback import format_exc; print format_exc()
            return HttpResponseServerError('failed')

    def move(self, request):
        u"""
        Перевести ученика в другой мастер-класс
        """

        ids = map(int, request.POST.get('ids', '').split(','))
        if not ids:
            return HttpResponse(200)

        students   = Students.objects.filter(pk__in=ids)
        new_class  = int(request.POST['newgroup'])
        old_class  = int(request.POST['gid'])
        errors = []
        moved = []

        for s in students:
            if not _add_student(new_class, s, group_list_orm=BonusClassList):
                errors.append(s.id)
            else:
                moved.append(s.id)

        _remove_student(old_class, set(ids) - set(errors), BonusClassList)

        return HttpResponse(json.dumps(
            {
                'moved': moved,
                'errors': errors
            }
        ))

    def delete_comment(self, request):
        Comments.objects.get(pk=request.POST['cid']).delete()
        return HttpResponse(200)

    def get_context_data(self, *args, **kwargs):

        now     = make_aware(datetime.datetime.now(), timezone(TIME_ZONE))
        context = super(BonusClassView, self).get_context_data(*args, **kwargs)
        mkid    = self.request.GET.get('id')
        mk      = BonusClasses.objects.select_related().get(pk=mkid)

        passes = {
            i.student.id: {
                'self': i.group,
                'repr': '%s c %s (%s)' % (i.group.dance_hall.station, i.group.start_date.strftime('%d.%m'), i.group.time_repr),
                'editable': i.start_date is None
            } for i in Passes.objects.filter(bonus_class_id=mk).only('group', 'student')
        }
        context['group_id'] = mkid
        context['students'] = [
            {
                'student': i.student,
                'group': passes.get(i.student.id),
                'attendance': i.attendance,
                'comments': json.dumps([
                    {'id': comment.id, 'text': comment.text, 'date': [
                        comment.add_date.year,
                        comment.add_date.month,
                        comment.add_date.day,
                        comment.add_date.hour,
                        comment.add_date.minute
                    ]} for comment in Comments.objects.filter(student=i.student).order_by('-add_date')
                ]) or '[]'
            }
            for i in BonusClassList.objects.select_related().filter(group=mk, active=True)
        ]
        context['groups'] = [
            dict(id=i.id, repr='%s c %s (%s)' % (i.dance_hall.station, i.start_date.strftime('%d.%m'), i.time_repr))
            for i in mk.available_groups.all()
        ]
        context['pass_types'] = mk.available_passes.all()
        context['future_classes'] = BonusClasses.objects.select_related().filter(Q(date__gte=now) | Q(pk=24)).order_by('date', 'time')
        context['within_group'] = mk.within_group.id if mk.within_group else None
        context['bonus_class'] = mk
        context['teachers'] = '-'.join(t.last_name for t in mk.teachers.all())

        return context

    def post(self, request, *args, **kwargs):
        try:
            action = getattr(self, request.POST['sub_action'])
            return action(request)

        except (AttributeError, KeyError):
            from traceback import format_exc
            print format_exc()
            return HttpResponseServerError('No method')

        except Exception:
            from traceback import format_exc
            print format_exc()
            return HttpResponseServerError('failed')


class HistoryView(BaseView):
    template_name = 'history.html'

    @staticmethod
    def __expire_check(qs):
        today = datetime.datetime.now().date()
        expire = datetime.timedelta(days=90)

        return filter(
            lambda g: today - g.end_date <= expire,
            qs
        )

    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        context['groups'] = self.__expire_check(Groups.closed.owner(self.request.user))

        if self.request.user.is_superuser:
            context['other_groups'] = self.__expire_check(Groups.closed.exclude_owner(self.request.user))

        context['user'] = self.request.user

        return context


class BonusClassHistoryView(BaseView):
    template_name = 'bkhistory.html'

    def get_context_data(self, **kwargs):
        now = datetime.datetime.now()
        context = super(BonusClassHistoryView, self).get_context_data(**kwargs)
        context['groups'] = BonusClasses.objects.filter(date__lte=now.date()).order_by('-date')
        print len(context['groups'])
        context['other_groups'] = []

        return context


class ClubCardsView(BaseView):

    template_name = 'club_cards.html'

    def get(self, *args, **kwargs):
        card_id = self.request.GET.get('id')

        if card_id:
            return self.get_card_detail(card_id)
        else:
            return super(ClubCardsView, self).get(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClubCardsView, self).get_context_data(**kwargs)
        date_format = '%d%m%Y'

        user = self.request.user
        now = datetime.datetime.now()
        date_from = datetime.datetime.strptime(self.request.GET['date'], date_format) if 'date' in self.request.GET\
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

        return context

    def get_card_detail(self, card_id):

        _pass = Passes.objects.get(pk=int(card_id))
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

        for group in get_student_groups(student):
            raise Exception
            if not group.end_date or (group.end_date and _pass.start_date <= group.end_date):
                date_from = _pass.start_date if _pass.start_date >= group.start_date else group.start_date
                date_to = group.end_date if group.end_date and group.end_date <= _pass.end_date else _pass.end_date
                days = get_count_of_weekdays_per_interval(group.days, date_from, date_to)
                group_calendar = filter(lambda x: x.date() <= date_to, group.get_calendar(days, date_from))
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


class PrintView(BaseView):
    date_format = '%d%m%Y'

    def __init__(self):
        super(PrintView, self).__init__()

        self.additional_contexts = {
            'lesson': self.lesson_context,
            'full': self.full_view_context
        }

    def lesson_context(self, context):
        self.template_name = 'print_lesson.html'
        date = datetime.datetime.strptime(self.request.GET['date'], self.date_format).date()
        group = Groups.objects.get(pk=self.request.GET['id'])

        context['group_name'] = group.name
        context['date'] = date.strftime('%d.%m.%Y')
        context['students'] = map(
            lambda s: dict(data=get_student_lesson_status(s, group, date), info=s),
            get_group_students_list(group)
        )

    def full_view_context(self, context):
        self.template_name = 'print_full.html'
        group_id = self.request.GET['id']
        date = self.request.GET.get('date')

        date_from = datetime.datetime.strptime(self.request.GET['date'], self.date_format) if date\
            else datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        date_to = get_last_day_of_month(date_from)

        context['date_str'] = '%s %d' % (MONTH_RUS[date_from.month], date_from.year)
        context['group_detail'] = get_group_detail(group_id, date_from, date_to, date_format='%d.%m.%y')

        context['subtype'] = self.request.GET.get('subtype', None)

        if not context['subtype']:
            raise TypeError('wrong subtype')

    def get_context_data(self, **kwargs):
        context = super(PrintView, self).get_context_data(**kwargs)

        html_color_classes = {
            key: val for val, key in get_color_classes()
        }
        context['passes_color_classes'] = [
            {'name': val, 'val': key} for key, val in html_color_classes.iteritems()
        ]

        self.additional_contexts[self.request['type']](context)

        return context


class GroupView(IndexView):
    template_name = 'group_detail.html'

    @staticmethod
    def check_available_days(days, dt1, dt2, cnt):
        return get_count_of_weekdays_per_interval(days, dt1, dt2) - 1 >= cnt

    def _edit_student_data(self, student_id, first_name=None, last_name=None, phone=None, org=False):
        try:
            student = Students.objects.get(pk=student_id)
            student.first_name = first_name.replace(' ', '')
            student.last_name = last_name.replace(' ', '')
            student.phone = check_phone(phone)
            student.org = org

            student.save()

        except Students.DoesNotExist:
            student = Students(
                first_name=first_name,
                last_name=last_name,
                phone=check_phone(phone),
                org=org
            )

            student.save()

    def delete_lessons(self, request):
        try:
            json_data = json.loads(request.POST['data'])
            student_id = json_data['stid']
            group_id = json_data['grid']
            date = datetime.datetime.strptime(json_data['date'], '%d.%m.%Y')
            count = json_data['cnt']

            lessons = list(Lessons.objects.filter(
                    group_id=group_id,
                    student_id=student_id,
                    date__gte=date
            ).order_by('date')[:count])

            passes = Counter([
                l.group_pass for l in lessons
            ])

            for group_pass, cnt in passes.most_common():
                current_count = len(Lessons.objects.filter(group_pass=group_pass))

                if group_pass.one_group_pass:
                    if current_count - cnt <= 0:
                        group_pass.delete()

                    else:
                        diff = (cnt if group_pass.lessons >= cnt else 0)
                        group_pass.lessons -= diff
                        group_pass.lessons_origin -= diff
                        group_pass.save()

                else:
                    group_pass.lessons = min(
                        group_pass.lessons.origin, group_pass.lessons + cnt
                    )
                    group_pass.save()


            for lesson in lessons:
                l.delete()

            return HttpResponse()

        except AssertionError:
            return HttpResponse()

        except Exception:
            from traceback import format_exc
            print format_exc()

            return HttpResponseServerError()

    def move_lessons(self, request):
        try:
            json_data = json.loads(request.POST['data'])
            student_id = json_data['stid']
            group_id = json_data['grid']
            date_from = datetime.datetime.strptime(json_data['date_from'], '%d.%m.%Y')
            date_to = datetime.datetime.strptime(json_data['date_to'], '%d.%m.%Y')

            p = Lessons.objects.get(student_id=student_id, group_id=group_id, date=date_from).group_pass
            wrapped = PassLogic.wrap(p)

            if not wrapped.freeze(date_from, date_to):
                raise Exception('Can\'t move lessons')

            return HttpResponse()

        except Exception:
            from traceback import format_exc
            print format_exc()

            return HttpResponseServerError()

    def save_student(self, request):
        try:
            json_data = json.loads(request.POST['data'])
            person = json_data['person']

            if person.get('id') is not None:
                self._edit_student_data(person['id'], person['first_name'], person['last_name'], person['phone'], person['org'])

            else:
                group = GroupLogic(int(json_data['group']))
                new_student_id = group.add_student(
                    first_name=person['first_name'],
                    last_name=person['last_name'],
                    phone=person['phone'],
                    org=person.get('org', False)
                )

            return HttpResponse(str(new_student_id))

        except Exception:
            from traceback import format_exc
            print format_exc()

            return HttpResponseServerError()

    def delete_student(self, request):
        try:

            json_data = json.loads(request.POST['data'])
            ids = json_data['ids']
            gid = json_data['gid']
            students = Students.objects.filter(pk__in=ids)
            errors = []

            if _remove_student(gid, ids, GroupList):
                return HttpResponse(200)
            else:
                return HttpResponseServerError('failed')


        except Exception:
            from traceback import format_exc
            print format_exc()

            return HttpResponseServerError()


    def cancel_lesson(self, request):
        try:
            json_data = json.loads(request.POST['data'])
            date = datetime.datetime.strptime(json_data['date'], '%d.%m.%Y')
            group_id = json_data['group']

            CanceledLessons(group_id=group_id, date=date).save()

            for _pass in (PassLogic.wrap(p) for p in Passes.objects.filter(
                    Q(start_date__lte=date) | Q(frozen_date__lte=date),
                    lessons__gt=0,
                    group_id=group_id,
            )):
                if _pass.check_date(date):
                    _pass.cancel_lesson(date)

                for lesson in _pass.lessons:

                    #TODO Переписать когда-нибудь!!!
                    if delete_debt(group_id, _pass.orm_object.student, lesson.date):
                        lesson.status = Lessons.STATUSES['attended']
                        lesson.save()

            return HttpResponse()

        except Exception:
            from traceback import format_exc
            print format_exc()

            return HttpResponseServerError()

    def restore_lesson(self, request):
        try:
            json_data = json.loads(request.POST['data'])
            date = datetime.datetime.strptime(json_data['date'], '%d.%m.%Y')
            group_id = json_data['group']

            for _pass in (PassLogic.wrap(p) for p in Passes.objects.filter(
                        Q(group_id=group_id),
                        Q(Q(start_date__lte=date) | Q(frozen_date__lte=date)),
                        Q(lessons__gt=0)
                )):
                    if _pass.check_date(date):
                        _pass.restore_lesson(date)

            CanceledLessons.objects.get(group_id=group_id, date=date).delete()

            return HttpResponse(200)

        except Exception:
            from traceback import format_exc
            print format_exc()
            return HttpResponseServerError('failed')

    def process_lesson(self, request):
        try:
            json_data = json.loads(request.POST['data'])
            group = Groups.all.get(pk=json_data['group_id'])
            date = datetime.datetime.strptime(json_data['date'], '%d.%m.%Y')
            teachers = map(int, json_data.get('teachers', []))

            for lesson in json_data['lessons']:
                if lesson['type'] == 'just_added':
                    nearest_lesson = Lessons.objects.filter(student_id=lesson['student_id'], group=group, date__gte=date).first()

                    # Долги
                    if lesson['pass_type_id'] == -2:
                        if date <= datetime.datetime.now() and not Debts.objects.filter(student_id=lesson['student_id'], group=group, date=date).exists():
                            debt = Debts(student_id=lesson['student_id'], group=group, date=date, val=0)
                            debt.save()

                    elif not nearest_lesson or self.check_available_days(group.days, date.date(), nearest_lesson.date, int(lesson['lessons_cnt'])):
                        pass_type = PassTypes.objects.get(pk=lesson['pass_type_id'])
                        new_pass = Passes(
                            student_id=lesson['student_id'],
                            group=group,
                            start_date=date,
                            pass_type=pass_type,
                            opener=request.user,
                            lessons=int(lesson['lessons_cnt']),
                            skips=int(lesson['skips_cnt']) if lesson['skips_cnt'] is not None else None,
                            creation_date=datetime.datetime.now().date()
                        )

                        new_pass.save()

                        wrapped_pass = PassLogic.wrap(new_pass)

                        debts = list(Debts.objects.filter(group=group, student_id=lesson['student_id'], date__lt=date).order_by('date'))

                        if len(debts) > 0:
                            new_pass.start_date = debts[0].date

                        i = new_pass.lessons
                        for debt in debts[:i]:
                            wrapped_pass.create_lessons(debt.date, 1, dates=[debt.date])
                            wrapped_pass.set_lesson_attended(debt.date, group=group)
                            i -= 1

                            comment = Comments(
                                student_id=lesson['student_id'],
                                group=group,
                                add_date=datetime.datetime.now(),
                                text='%s - Списан долг за счет абонемента от %s' % (debt.date.strftime('%d.%m.%Y'), date.strftime('%d.%m.%Y'))
                            )
                            comment.save()
                            debt.delete()

                        new_pass.lessons = i
                        new_pass.save()
                        wrapped_pass.create_lessons(date, new_pass.lessons, group=group)
                        wrapped_pass.set_lesson_attended(date, group=group)

                elif lesson['type'] == 'pass':
                    lesson_pass = PassLogic.wrap(Passes.objects.get(pk=lesson['pid']))

                    if lesson['attended']:
                        lesson_pass.set_lesson_attended(date, group=group)
                    elif json_data['setMisses']:
                        lesson_pass.set_lesson_not_attended(date)

            if len(teachers) > 0:
                if set(map(int, group.teachers.all().values_list('pk', flat=True))) != set(teachers):
                    try:
                        subst = TeachersSubstitution.objects.get(group=group, date=date)
                        subst.teachers.remove(*subst.teachers.all())
                        subst.teachers.add(*User.objects.filter(pk__in=teachers))

                    except TeachersSubstitution.DoesNotExist:
                        try:
                            subst = TeachersSubstitution(
                                group=group,
                                date=date
                            )
                            subst.save()
                            subst.teachers.add(*User.objects.filter(pk__in=teachers))
                        except:
                            from traceback import format_exc
                            print format_exc()

                            subst.delete()
                else:
                    try:
                        subst = TeachersSubstitution.objects.get(
                            group=group,
                            date=date
                        )
                        subst.delete()
                    except TeachersSubstitution.DoesNotExist:
                        pass

        except Exception:
            from traceback import format_exc
            print format_exc()

            return HttpResponseServerError()

        return HttpResponse()

# 1. Только добавили
# 2. Отмечание занятия

    @request_handler
    def move_to_trash(self, gid, ids):
        group = GroupLogic(gid)
        for _id in ids:
            try:
                al_rec = AdministratorList.objects.get(student_id=_id)

            except AdministratorList.DoesNotExist:
                al_rec = AdministratorList(student_id=_id)
                al_rec.save()

            if group not in al_rec.groups.all():
                al_rec.groups.add(group.orm)

            group.delete_student(_id)


    def rest_process_subst(self, *args, **kwargs):
        """
        REST method for process teachers substitutions
        """
        request_data = json.loads(self.request.POST['data'])
        group = Groups.objects.get(pk=request_data['group_id'])

        for _date, teachers in request_data['substitutions'].iteritems():
            s_date = datetime.datetime.strptime(_date, '%d.%m.%Y')
            qs = TeachersSubstitution.objects.filter(date=s_date, group=group)
            qs.delete()

            if set(group.teachers.only('pk')) != teachers:
                new_subst = TeachersSubstitution(
                    date=s_date.date(),
                    group=group
                )
                new_subst.save()
                new_subst.teachers.add(*User.objects.filter(pk__in=teachers))

        return HttpResponse("OK")

    @cached_property
    def html_color_classes(self):
        return {
            key: val for val, key in get_color_classes()
        }

    def process_comment(self, request):
        json_data = json.loads(request.POST['data'])
        cid = json_data.get('cid')
        action_type = json_data['type']

        if action_type == 'add':
            comment = Comments(
                student_id=json_data['stid'],
                group_id=json_data['grid'],
                add_date=datetime.datetime.now(),
                text=json_data['msg']
            )
            comment.save()

            return HttpResponse(comment.pk)

        elif cid is not None and action_type == 'edit':
            comment = Comments.objects.filter(pk=cid).update(
                text=json_data['msg'],
                add_date=datetime.datetime.now()
            )

        elif cid is not None and action_type == 'delete':
            try:
                Comments.objects.get(pk=cid).delete()

            except Comments.DoesNotExist:
                pass

        return HttpResponse("ok")

    def get_detail_repr(self, obj):
        if isinstance(obj, GroupLogic.CanceledLesson):
            return {
                'type': 'canceled',
                'pass': False,
                'color': '',
                'sign': '',
                'attended': False,
                'canceled': True
            }

        elif isinstance(obj, GroupLogic.PhantomLesson):
            return {
                'type': 'pass',
                'pass': True,
                'sign': '',
                'sign_type': 's',
                'attended': Lessons.STATUSES['not_processed'],
                'pid': obj.group_pass.id,
                'first': False,
                'last': False,
                'color': self.html_color_classes[obj.group_pass.color]
            }

        elif isinstance(obj, Lessons):
            return {
                'type': 'pass',
                'pass': True,
                'sign': obj.sign,
                'sign_type': 's' if isinstance(obj.sign, str) else 'n',
                'attended': obj.status == Lessons.STATUSES['attended'],
                'pid': obj.group_pass.id,
                'first': self.group.lesson_is_last_in_pass(obj),
                'last': self.group.lesson_is_first_in_pass(obj),
                'color': '' if obj.status == Lessons.STATUSES['moved'] else self.html_color_classes[obj.group_pass.color] if not obj.student.org  else ORG_PASS_HTML_CLASS
            }

        else:
            return {
                'type': None,
                'pass': False,
                'color': 'text-error' if isinstance(obj, Debts) else '',
                'sign': 'долг' if isinstance(obj, Debts) else '',
                'sign_type': 's' if isinstance(obj, Debts) else '',
                'attended': False,
                'canceled': False,
                'first': False,
                'last': False,
                'debt': isinstance(obj, Debts)
            }

    def get_context_data(self, **kwargs):
        def to_iso(elem): # deprecated
            elem['date'] = elem['date'].strftime('%d.%m.%Y')

            return elem

        now = datetime.datetime.now()
        date_format = '%m%Y'
        _, group_id, request_date = (self.request.path.split('/')[1:] + [None] * 3)[:3]

        if request_date:
            request_date = datetime.datetime.strptime(request_date, date_format)

        self.group = group = GroupLogic(int(group_id), request_date)

        forward_month = (get_last_day_of_month(now) + datetime.timedelta(days=1)).date()
        if group.last_lesson_ever:
            forward_month = max(forward_month, group.last_lesson_ever.date)

        border = datetime.datetime.combine(group.orm.start_date, datetime.datetime.min.time()).replace(day=1)

        context = super(GroupView, self).get_context_data(**kwargs)
        context['passes_color_classes'] = [
            dict(name=n, val=v) for n, v in get_color_classes()
        ]
        context['control_data'] = json.dumps({
            'constant': {
                'current_date_str': '%s %d' % (MONTH_RUS[group.date_1.month], group.date_1.year),
                'current_date_numval': group.date_1.strftime(date_format)
            },
            'date_control': map(
                lambda d: {'name': '%s %d' % (MONTH_RUS[d.month], d.year), 'val': "%s/%s" % (group_id, d.strftime(date_format))},
                filter(
                    lambda x1: x1 >= border,
                    map(lambda x: get_month_offset(forward_month, x), xrange(0, 8))
                )
            )
        })

        day_balance, totals = group.calc_money()
        _request_date = request_date.date() if request_date else None
        students = [
            {
                'person': s['student'].__json__(),
                'is_newbie': s['student'].pk in group.newbies,
                'calendar': map(self.get_detail_repr, s['lessons']),  #get_student_calendar(s, group, date_from, dates_count, '%d.%m.%Y'),
                'debt': len(s['debts']) > 0,
                'pass_remaining': s['pass_remaining'],
                'comments': map(lambda x: x.__json__(), s['comments'] if s['comments'] else []),
                'lessons_count': len([
                    l for l in s['lessons'] if l is not None or (_request_date or group.orm.start_date) >= now.date()
                ])
            } for s in group.get_students_net()
        ]

        if self.request.user.is_superuser:
            profit = group.profit()
            bad_profit = [day for day, val in profit if val == -1]
            normal_profit = [day for day, val in profit if val == 0]
            good_profit = [day for day, val in profit if val == 1]

        else:
            bad_profit = normal_profit = good_profit = []

        real_group_calendar = [k['date'].date() for k in group.calcked_calendar]

        period_begin, period_end = (lambda x: x[0::len(x)-1])(group.calcked_calendar)

        club_cards = [p.__json__() for p in Passes.objects\
            .filter(
                pass_type__one_group_pass=0,
                start_date__lte=period_end['date'],
                end_date__gte=period_begin['date'],
                lessons__gt=0
            ).select_related('student').order_by('student__last_name', 'student__first_name')\
            .order_by('-start_date')]

        for det in club_cards:
            det['html_color_class'] = self.html_color_classes.get(det.get('color'))

        context['group_detail'] = json.dumps({
            'group_data': group.__json__(),
            #'id': group.id,
            #'name': group.name,
            #'days': group.days,
            #'days_str': '-'.join(group.orm.days),
            #'station': group.orm.dance_hall.station,
            #'time': group.orm.time,
            #'start_date': group.start_date,
            'students': students,
            'active_students': filter(lambda s: s['lessons_count'] > 0, students),
            'not_active_students': filter(lambda s: s['lessons_count'] == 0, students),
            'last_lesson': group.last_lesson.strftime('%d.%m.%Y'),
            'club_cards' : club_cards,
            'calendar': [{
                'date': i.strftime('%d.%m.%Y'),
                'canceled': i in group.canceled_lessons,
                'real_date': i in real_group_calendar,
                'profit': 1 if i in good_profit \
                     else 0 if i in normal_profit \
                     else -1 if i in bad_profit \
                     else None
            } for i in group.calendar],
            'moneys': day_balance,
            'money_total': totals
        })

        salary = defaultdict(list)
        for i in day_balance:
            for k, v in i['salary'].iteritems():
                salary[k].append(v)

        context['group'] = self.group
        context['salary'] = salary.items()

        context['pass_detail'] = [
            p.__json__()
            for p in PassTypes.all.filter(pk__in=group.available_passes.all()).order_by('sequence')
        ] + [
            {'id': -2, 'name': 'Долг'}
        ]
        context['other_groups'] = Groups.opened.exclude(id=group.id)

        for elem in context['pass_detail']:
            elem['skips'] = elem.get('skips', '')

        for det in context['pass_detail']:
            det['html_color_class'] = self.html_color_classes.get(det.get('color'))

        context['pass_detail'] = json.dumps(context['pass_detail'])

        context['teachers_cnt'] = xrange(len(group.orm.teachers.all()))
        context['teachers'] = json.dumps(dict(
            (u.pk, u.__json__()) for u in User.objects.filter(Q(teacher=True) | Q(assistant=True))
        ))
        context['default_teachers'] = '-'.join(t.last_name for t in group.orm.teachers.all())

        _substitutions = [
            map(lambda v: v.pk, val)
            for _, val in sorted(group.substitutions.iteritems(), key=lambda k: k[0])
        ]
        context['substitutions'] = json.dumps(_substitutions)

        default_teachers_cnt = len(group.orm.teachers.all())
        context['raw_substitutions'] = (
            (date.strftime('%d.%m.%Y'), (list(teachers) + [None] * default_teachers_cnt)[:default_teachers_cnt])
            for date, teachers in sorted(group.substitutions.iteritems(), key=lambda x: x[0])
        )
        context['default_tachers_cnt'] = default_teachers_cnt

        return context


class FinanceView(BaseView):

    template_name = 'finance.html'

    def get_context_data(self, **kwargs):
        context = super(FinanceView, self).get_context_data(**kwargs)

        if 'date' in self.request.GET:
            date1 = datetime.datetime.strptime('01' + self.request.GET['date'], '%d%m%Y')
        else:
            date1 = datetime.datetime.now().replace(day=1)

        date1 = datetime.datetime(2017, 2, 1)
        date2 = get_last_day_of_month(date1)

        groups = Groups.all.filter(
            Q(end_date__isnull=True) | Q(end_date__gte=date1),
            start_date__lte=date2
        ).order_by('dance_hall__station', '_days', 'time')

        data = [
            (group, GroupLogic(group, date1).calc_money()[-1])
            for group in groups
        ]

        sal = defaultdict(list)
        group_totals = dict.fromkeys([
           'day_total',
            'dance_hall',
            'club',
            'next_month_balance'
        ], 0)

        for group, salary_data in data:
            for teacher, salary_val in salary_data['salary'].iteritems():
                sal[teacher].append((group, salary_val))

            for key, val in salary_data.iteritems():
                if key in group_totals.keys():
                    group_totals[key] += val

        data.append((
            dict(name=u"ИТОГО"),
            group_totals
        ))

        for teacher, teacher_salary_details in sal.iteritems():

            val = [
                v[1] for v in teacher_salary_details
            ]

            s1 = sum([
                v['count'] for v in val
            ])

            s2 = sum([
                v['compensation'] for v in val
            ])

            sal[teacher].append(
                ({'name': u'ИТОГО', 'dance_hall': ''}, {'count': s1, 'compensation': s2})
            )

        context['interval'] = '%s - %s' % (date1.strftime('%d.%m.%Y'), date2.strftime('%d.%m.%Y'))
        context['finance_data'] = data
        context['sal'] = dict(sal)

        return context


class AdminCallsView(BaseView):
    template_name = u'admin_calls.html'

    @staticmethod
    def serial(student, group, reason, issues, group_pass=None):

        student_issues = issues.get((student, group, group_pass))

        if student_issues:
            _issue = list(student_issues)[-1]
            return {
                'student': student.__json__(),
                'group': group.__json__(),
                'answer': {
                    'type': _issue.responce_type,
                    'userMessage': _issue.message.text,
                    'val': _issue.message.text,
                    'date': _issue.date.strftime('%d.%m.%Y')
                },
                'group_pass': {
                    'id': group_pass.pk if group_pass else None
                },
                'reason': reason,
                'issue_id': _issue.pk
            }

        else:
            return {
                'student': student.__json__(),
                'group': group.__json__(),
                'reason': reason,
                'group_pass': {
                    'id': group_pass.pk if group_pass else None
                }
            }

    def get_list(self, qs, msg, issues):
        serial = lambda s: self.serial(s.student, s.group, msg, issues, s.group_pass if isinstance(s, Lessons) else None)
        return map(serial, qs)

    def get_context_data(self, **kwargs):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        context = super(AdminCallsView, self).get_context_data(**kwargs)
        call_list = []

        tomorrow_bonus_class = BonusClasses.objects.filter(date=tomorrow)
        tomorrow_new_groups = Groups.objects.filter(start_date=tomorrow)
        tomorrow_groups = Groups.opened.filter(
            Q(end_date__gt=tomorrow) | Q(end_date=None),
            _days__contains=str(tomorrow.weekday()),
        )
        today_groups = Groups.opened.filter(_days__contains=str(today.weekday()))

        issues = defaultdict(list)
        for issue in AdminCalls.objects.all(
            #Q(group__in=tomorrow_groups) | Q(group__in=tomorrow_new_groups)
        ).order_by('date', 'id'):

            issues[(issue.student, issue.group, issue.group_pass)].append(issue)

        call_list += self.get_list(
            BonusClassList.objects.filter(group__in=tomorrow_bonus_class).order_by("group", "student__last_name"),
            u"Посещение ОУ",
            issues
        )

        call_list += self.get_list(
            GroupList.objects.filter(group__in=tomorrow_new_groups).order_by("group", "student__last_name"),
            u"Посещение завтрашнего занятия в группе",
            issues
        )

        call_list += self.get_list(
            self._get_fired_passes(tomorrow_groups, tomorrow, issues),
            u"Сгорает абонемент",
            issues
        )

        call_list += self.get_list(
            self._get_loosers(tomorrow_groups, tomorrow),
            u"Перестал(a) ходить",
            issues
        )

        call_list += self.get_list(
            self._not_come_yet(tomorrow, tomorrow_groups, tomorrow_new_groups),
            u"Записался(лась) и не ходит",
            issues
        )

        _filter = []
        for issue in AdminCalls.objects.filter(
            responce_type__in=["waitListByDate", "waitListDefault"]
        ).exclude(
            pk__in=AdminCalls.objects.filter(
                Q(group__in=tomorrow_groups) | Q(group__in=tomorrow_new_groups)
        ).values_list('pk', flat=True)).order_by('-date', '-id'):

            if (issue.student, issue.group) in _filter:
                continue
            elif issue.responce_type == "waitListDefault" \
                    or (issue.responce_type == "waitListByDate" \
                        and datetime.datetime.strptime(issue.message.text.split()[-1], '%d.%m.%Y') == today):
                call_list += self.get_list(
                    [issue],
                    u"Лист ожидания",
                    {(issue.student, issue.group, None): [issue]}
                )

            _filter.append((issue.student, issue.group))

        call_list.sort(key=lambda x: (x['student']['last_name'], x['student']['first_name']))

        context['call_list'] = json.dumps(call_list)

        context['students_data'] = json.dumps([
            s.__json__()
            for s in Students.objects.all()[:10]
        ])


        return context

    def _get_fired_passes(self, groups, date, issues):
        u"""
        Сгорающие абонементы
        """

        groups_last_lessons = [group.get_calendar(-2, date)[-1] for group in groups]
        result = []
        _filter = []

        _f = Q()

        for _g in groups:
            _f |= Q(group=_g, date=_g.get_calendar(-2, date)[-1])

        na_lessons = Lessons.objects.filter(
            _f,
            status=Lessons.STATUSES['not_attended'],
            group_pass__lessons__gt=0
        ).order_by('-date')

        for lesson in na_lessons:
            if (lesson.student, lesson.group) in _filter:
                continue

            _filter.append((lesson.student, lesson.group))

            issue = issues.get((lesson.student, lesson.group, lesson.group_pass))

            real_lessons = Lessons.objects.filter(
                group_pass=lesson.group_pass,
                status__in=[Lessons.STATUSES['attended'], Lessons.STATUSES['not_attended']]
            ).count()

            if real_lessons >= lesson.group_pass.lessons_origin:
                continue

            elif issue is not None:
                _qs = Lessons.objects.filter(
                    group_pass=lesson.group_pass, date__range=[issue[-1].date, date]
                ).exclude(status=Lessons.STATUSES['not_attended'])

                if len(_qs) > 0 and self.check_relevant(lesson, issue[-1], date - datetime.timedelta(days=1)):
                    result.append(lesson)
            else:
                result.append(lesson)

        return result

    def _not_come_yet(self, date, groups, tomorrow_new_groups):
        people = GroupList.objects.filter(
            group__in=groups,
            active=True
        ).exclude(
            student_id__in=Lessons.objects.filter(group__in=groups).values_list('student_id', flat=True)
        ).exclude(
            group__in=tomorrow_new_groups
        ).exclude(
            student_id__in=AdminCalls.objects.filter(
                responce_type__in=["refusal"]
            ).values_list('student_id', flat=True)
        )

        return people

    def _get_loosers(self, groups, date):
        u"""
        Люди, которые перестали ходиь на группы
        """

        group_cache = dict()
        student_cache = dict()

        def lesson_wrapper(group_id, student_id):
            group = group_cache.get(group_id)

            if not group:
                group = group_cache[group_id] = Groups.objects.get(pk=group_id)

            student = student_cache.get(student_id)

            if not student:
                student = student_cache[student_id] = Students.objects.get(pk=student_id)

            wrapper = namedtuple('Lesson', ['group', 'student'])

            return wrapper(group, student)

        borders = dict(
            (group.id, map(lambda x: x.date(), group.get_calendar(-4, date)[-1:]))
             for group in groups
        )

        lessons = [
            lesson_wrapper(lesson['group'], lesson['student'])
            for lesson in Lessons.objects.filter(group__in=groups).values('group', 'student').annotate(max_date=Max('date'))
            if lesson['max_date'] in borders[int(lesson['group'])]
                and not Debts.objects.filter(student_id=lesson['student'], group_id=lesson['group'], date__gt=lesson['max_date']).exists()
        ] + [
            lesson_wrapper(debt['group'], debt['student'])
            for debt in Debts.objects.filter(group__in=groups).values('group', 'student').annotate(max_date=Max('date'))
            if debt['max_date'] in borders[int(debt['group'])]
                and not Lessons.objects.filter(student_id=debt['student'], group_id=debt['group'], date__gt=debt['max_date']).exists()
        ]

        return lessons

    @staticmethod
    def check_relevant(lesson, issue, date):
        if issue is not None:
            if issue.responce_type in ('comming_date', 'waitListByDate'):
                try:
                    s_date = issue.message.text.split()
                    _date = datetime.datetime.strptime(s_date[-1], '%d.%m.%Y').date()
                    return _date < date
                except UnicodeEncodeError:
                    return True

            elif issue.responce_type == 'refusal':
                return False

            else:
                return True

    def process_call(self, request, *args, **kwargs):
        request_data = json.loads(request.POST.get('data'))
        issue_id = request_data.get('issue_id')

        if issue_id is not None:
            issue = AdminCalls.objects.filter(pk=issue_id)

            if request_data['answer'] is not None:
                comment = Comments(
                    add_date = datetime.datetime.now(),
                    student_id = request_data['st_id'],
                    group_id=request_data['group_id'],
                    text=request_data['answer']['userMessage']
                )
                comment.save()
            else:
                return HttpResponse(200)

            new_issue = AdminCalls(
                **issue.values('student_id', 'group_id', 'group_pass_id', 'responce_type', 'caller_id', 'is_solved')[0]
            )
            new_issue.date = datetime.datetime.today()
            new_issue.responce_type = request_data['answer']['type'] if request_data['answer'] else None
            new_issue.message = comment
            new_issue.related_call = issue.first()
            new_issue.save()
        else:

            comment = Comments(
                add_date = datetime.datetime.now(),
                student_id = request_data['st_id'],
                group_id=request_data['group_id'],
                text=request_data['answer']['userMessage']
            )

            comment.save()

            new_issue = AdminCalls(
                date=datetime.datetime.today(),
                student_id=request_data['st_id'],
                group_id=request_data['group_id'],
                group_pass_id=request_data.get('group_pass'),
                responce_type=request_data['answer']['type'],
                message=comment,
                caller=request.user
            )
            new_issue.save()

        return HttpResponse(200)


class AdministratorView(IndexView):
    """
    Вьюшка для списка-помойки
    """

    template_name = u'admin_list.html'

    @request_handler
    def save_comment(self, st_id, text):
        try:
            request_data = json.loads(request.POST.get('data'))

            comment = Comments(
                add_date = datetime.datetime.now(),
                student_id = request_data['st_id'],
                text=request_data['text']
            )

            comment.save()

            return HttpResponse('OK')

        except Exception:
            return HttpResponseServerError()

    @request_handler
    def move_student(self, stid, gid):
        GroupLogic(gid).add_student_simple(Students.objects.get(pk=stid))

    @request_handler
    def delete_student(self, st_id, fulldelete):
        if fulldelete:
            AdministratorList.objects.get(student_id=int(st_id)).delete()
        else:
            AdministratorList.objects.filter(student_id=int(st_id)).update(
                status=AdministratorList.STATUSES["simple_deleted"]
            )

    def get_context_data(self, *args, **kwargs):

        """
        [
            {
                student: student.__json__(),
                groups: [
                    group1.__json__(),
                    group2.__json__(),
                ]
                comments: [
                    comment1.__json__(),
                    comment2.__json__()
                ]
            },
            {
                ...
            }
        ]
        """

        context = super(AdministratorView, self).get_context_data(**kwargs)

        data = AdministratorList.objects.select_related().filter(
            status=AdministratorList.STATUSES['active']
        )

        comments_filter = [
            Q(group=group, student=rec.student)
            for rec in data for group in rec.groups.all()
        ] + [
            Q(group=None)
        ]

        if not comments_filter:
            comments = ()

        else:
            comments = Comments.objects.filter(reduce(
                lambda a, x: a | x,
                comments_filter[1:],
                comments_filter[0]
            )).order_by('add_date')

        context['data'] = []

        for record in data:
            context_rec = dict(
                student=record.student.__json__(),
                groups=[group.__json__() for group in record.groups.all()],
                comments=[comment.__json__() for comment in comments if comment.student == record.student]
            )

            context['data'].append(context_rec)

        context['data'] = json.dumps(context['data'])

        groups = [
            g.__json__()
            for g in Groups.opened.all().order_by('level')
        ]
        context['groups'] = json.dumps(groups)

        return context
