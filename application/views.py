# -*- coding:utf-8 -*-
import datetime
from django.shortcuts import render_to_response
from auth import check_auth
from django.template import RequestContext
from django.template.context_processors import csrf
from django.db.models import Q

from application.utils.passes import get_color_classes
from application.utils.groups import get_groups_list, get_group_detail

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


def group_detail_view(request):

    context = {}
    template = 'group_detail.html'

    group_id = int(request.GET['id'])

    test = [
        datetime.datetime(2015, 6, 1),
        datetime.datetime(2015, 6, 30)
    ]

    context['single_pass_id'] = PassTypes.objects.filter(name__iregex='Разовое занятие').values('id')

    context['passes_color_classes'] = [
        {'name': key, 'val': val} for key, val in get_color_classes()
    ]
    context['group_detail'] = get_group_detail(group_id, test[0], test[1])
    context['pass_detail'] = PassTypes.objects.all()

    return render_to_response(template, context, context_instance=RequestContext(request, processors=[custom_proc]))