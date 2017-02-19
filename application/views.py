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
from django.db.models import Sum, Q
from django.utils.functional import cached_property

from application.logic.student import add_student as _add_student, remove_student as _remove_student, edit_student as _edit_student
from application.logic.group import GroupLogic

from application.utils.passes import get_color_classes, PassLogic, ORG_PASS_HTML_CLASS
from application.utils.groups import get_groups_list, get_group_detail, get_student_lesson_status, get_group_students_list, get_student_groups
from application.utils.date_api import get_month_offset, get_last_day_of_month, MONTH_RUS
from application.models import Lessons, User, Passes, GroupList, SampoPayments, SampoPasses, SampoPassUsage, Debts, GroupLevels, TeachersSubstitution
from application.auth import auth_decorator
from application.utils.date_api import get_count_of_weekdays_per_interval
from application.utils.sampo import get_sampo_details, write_log

from models import Groups, Students, User, PassTypes, BonusClasses, BonusClassList, Comments # todo ненужный импорт
from collections import namedtuple, defaultdict


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
        context['pass_detail'] = PassTypes.all.filter(one_group_pass=True, pk__in=group.available_passes).order_by('sequence').values()
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
                return HttpResponseServerError()

        else:
            return HttpResponseServerError('wrong action name')



class IndexView(BaseView):
    template_name = 'main_view.html'

    class Url(object):
        """
        Класс для создания обыкновенных ссылок на странице
        """
        def __init__(self, label, url):
            self.label = label
            self.url = url

    def get(self, *args, **kwargs):
        user = self.request.user

        #Если пользователь - админ сампо, отправляем его на другую вьюшку
        if user.teacher:
            return super(IndexView, self).get(self.request, *args, **kwargs)

        elif user.sampo_admin:
            return redirect('/sampo')

        else:
            # Всех остальных - лесом!
            return HttpResponseServerError(403)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['now'] = datetime.datetime.now().date()

        depth = 1
        menu = []
        user = self.request.user

        # Меню для руководства
        if user.is_superuser:
            groups = Groups.opened

            # Мои группы
            menu.append({
                'label':u'Мои группы',
                'depth': str(depth),
                'hideable': False,
                'urls': groups.filter(teachers=user)
            })

            # Группы других преподавателей
            depth += 1
            menu.append({
                'label': u'Остальные группы',
                'depth': str(depth),
                'hideable': False,
                'urls': [
                    {
                        'label': level.name,
                        'hideable': True,
                        'depth': '%d_%d' % (depth, level_depth),
                        'urls': groups.filter(level=level).exclude(teachers=user)
                    } for level_depth, level in enumerate(GroupLevels.objects.all())
                ]
            })

            #Мастер-классы
            depth += 1
            menu.append({
                'label': u'Мастер-классы',
                'depth': str(depth),
                'hideable': True,
                'url_pattern': 'mk',
                'urls': [b for b in BonusClasses.objects.select_related().filter(date__gte=context['now']).order_by('-date')] + [self.Url(u'-- все прошедшие классы', 'bkhistory')]
            })

            #Закрытые группы
            depth += 1
            menu.append({
                'label': u'Закрытые группы',
                'depth': str(depth),
                'hideable': True,
                'urls': [g for g in Groups.closed.all().order_by('-end_date')[:5]] + [self.Url(u'--все закрытые группы--', 'history')]
            })

        # Меню для других преподов
        else:
            # Мои группы
            menu.append({
                'label': u'Группы',
                'depth': str(depth),
                'hideable': False,
                'urls': Groups.opened.filter(teachers=user)
            })

            #Мастер-классы
            depth += 1
            menu.append({
                'label': u'Мастер-классы',
                'depth': str(depth),
                'hideable': True,
                'urls': BonusClasses.objects.select_related().filter(teachers=user).order_by('-date')
            })

            #Закрытые группы
            depth += 1
            menu.append({
                'label': u'Закрытые группы',
                'depth': str(depth),
                'hideable': True,
                'urls': [g for g in Groups.closed.filter(teachers=user).order_by('-end_date')[:5]] + [self.Url(u'--все закрытые группы--', 'history')]
            })

        #Общеклубное меню
        depth += 1
        menu.append({
            'label': u'Клуб',
            'depth': str(depth),
            'hideable': False,
            'urls': [self.Url(u'Клубные карты', 'clubcards'), self.Url(u'САМПО', 'sampo')]
        })

        context['menu'] = menu

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
                request.POST['e_mail'],
                request.POST.get('is_org')
            )

        else:
            _json = _add_student(
                request.POST['gid'],
                (request.POST['first_name'], request.POST['last_name'], request.POST['phone']),
                request.POST['e_mail'],
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

        for group in get_student_groups(student, opened_only=True):

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


class GroupView(BaseView):
    template_name = 'group_detail.html'

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

    def get_detail_repr(self, obj):
        if isinstance(obj, GroupLogic.CanceledLesson):
            return {
                'pass': False,
                'color': '',
                'sign': '',
                'attended': False,
                'canceled': True
            }

        elif isinstance(obj, GroupLogic.PhantomLesson):
            return {
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
                'pass': False,
                'color': 'text-error' if isinstance(obj, Debts) else '',
                'sign': 'долг' if isinstance(obj, Debts) else '',
                'sign_type': 's' if isinstance(obj, Debts) else '',
                'attended': False,
                'canceled': False,
                'first': False,
                'last': False
            }

    def get_context_data(self, **kwargs):
        def to_iso(elem): # deprecated
            elem['date'] = elem['date'].strftime('%d.%m.%Y')

            return elem

        now = datetime.datetime.now()
        date_format = '%d%m%Y'

        try:
            request_date = datetime.datetime.strptime(self.request.GET['date'], date_format)
        except KeyError:
            request_date = None

        self.group = group = GroupLogic(self.request.GET['id'], request_date)

        forward_month = (get_last_day_of_month(now) + datetime.timedelta(days=1)).date()
        if group.last_lesson_ever:
            forward_month = max(forward_month, group.last_lesson_ever.date)

        border = datetime.datetime.combine(group.orm.start_date, datetime.datetime.min.time()).replace(day=1)

        context = super(GroupView, self).get_context_data(**kwargs)
        context['passes_color_classes'] = [
            dict(name=n, val=v) for n, v in get_color_classes()
        ]
        context['control_data'] = {
            'constant': {
                'current_date_str': '%s %d' % (MONTH_RUS[group.date_1.month], group.date_1.year),
                'current_date_numval': group.date_1.strftime(date_format)
            },
            'date_control': map(
                lambda d: {'name': '%s %d' % (MONTH_RUS[d.month], d.year), 'val': d.strftime(date_format)},
                filter(
                    lambda x1: x1 >= border,
                    map(lambda x: get_month_offset(forward_month, x), xrange(0, 8))
                )
            )
        }

        day_balance, totals = group.calc_money()
        students = [
            {
                'person': s['student'],
                'is_newbie': s['student'].pk in group.newbies,
                'calendar': map(self.get_detail_repr, s['lessons']),  #get_student_calendar(s, group, date_from, dates_count, '%d.%m.%Y'),
                'debt': len(s['debts']) > 0,
                'pass_remaining': s['pass_remaining'],
                'last_comment': s['last_comment']
            } for s in group.get_students_net()
        ]

        real_group_calendar = [k['date'].date() for k in group.calcked_calendar]
        context['group_detail'] = {
            'id': group.id,
            'name': group.name,
            'days': group.days,
            'start_date': group.start_date,
            'students': students,
            'last_lesson': group.last_lesson,
            'calendar': [{
                'date': i.strftime('%d.%m.%Y'),
                'canceled': i in group.canceled_lessons,
                'real_date': i in real_group_calendar
            } for i in group.calendar],
            'moneys': day_balance,
            'money_total': totals
        }

        salary = defaultdict(list)
        for i in day_balance:
            for k, v in i['salary'].iteritems():
                salary[k].append(v)

        context['salary'] = salary.items()


        context['pass_detail'] = PassTypes.all.filter(one_group_pass=True, pk__in=group.available_passes.all()).order_by('sequence').values()
        context['other_groups'] = Groups.opened.exclude(id=group.id)

        for elem in context['pass_detail']:
            elem['skips'] = '' if elem['skips'] is None else elem['skips']

        for det in context['pass_detail']:
            det['html_color_class'] = self.html_color_classes[det['color']]

        context['teachers_cnt'] = xrange(len(group.orm.teachers.all()))
        context['teachers'] = User.objects.filter(Q(teacher=True) | Q(assistant=True))
        context['substitutions'] = json.dumps(dict((
            (key.strftime('%d.%m.%Y'), map(lambda x: x.pk, val))
            for key, val in group.substitutions.iteritems()
        )))

        default_teachers_cnt = len(group.orm.teachers.all())
        context['raw_substitutions'] = (
            (date.strftime('%d.%m.%Y'), (list(teachers) + [None] * default_teachers_cnt)[:default_teachers_cnt])
            for date, teachers in sorted(group.substitutions.iteritems(), key=lambda x: x[0])
        )
        context['default_tachers_cnt'] = default_teachers_cnt

        return context

