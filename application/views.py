# -*- coding:utf-8 -*-
import datetime
from django.shortcuts import render_to_response, redirect
from auth import check_auth, log_out
from django.template import RequestContext
from django.template.context_processors import csrf

from application.utils.passes import get_color_classes
from application.utils.groups import get_groups_list, get_group_detail
from application.utils.date_api import get_month_offset, get_last_day_of_month, MONTH_RUS

from models import Groups, Students, User, PassTypes


def custom_proc(request):
    "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'My app',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def index_view(request):

    user = check_auth(request)
    main_template = 'main_view.html'
    login_template = 'login.html'

    if user:
        context = {}
        context['user'] = user
        context['groups'] = get_groups_list(user)

        return render_to_response(main_template, context, context_instance=RequestContext(request, processors=[custom_proc]))

    else:
        args = {}
        args.update(csrf(request))
        return render_to_response(login_template, args, context_instance=RequestContext(request, processors=[custom_proc]))


def user_log_out(request):
    log_out(request)
    return redirect('/')


def group_detail_view(request):

    context = {}
    template = 'group_detail.html'
    date_format = '%d%m%Y'

    group_id = int(request.GET['id'])
    date_from = datetime.datetime.strptime(request.GET['date'], date_format) if 'date' in request.GET\
        else datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    date_to = get_last_day_of_month(date_from)
    now = datetime.datetime.now()

    context['control_data'] = {
        'constant': {
            'current_date_str': '%s %d' % (MONTH_RUS[date_from.month], date_from.year),
            'current_date_numval': date_from.strftime(date_format)
        },
        'date_control': map(
            lambda d: {'name': '%s %d' % (MONTH_RUS[d.month], d.year), 'val': d.strftime(date_format)},
            map(lambda x: get_month_offset(now.date().replace(day=1), x), xrange(0, 7))
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
    context['pass_detail'] = PassTypes.objects.all().values()

    for det in context['pass_detail']:
        det['html_color_class'] = html_color_classes[det['color']]

    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))