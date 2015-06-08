# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response
from auth import check_auth
from django.template import RequestContext
from django.template.context_processors import csrf
from django.db.models import Q

from models import Groups, Students, User


def custom_proc(request):
    "A context processor that provides 'app', 'user' and 'ip_address'."
    return {
        'app': 'My app',
        'user': request.user,
        'ip_address': request.META['REMOTE_ADDR']
    }


def index(request):

    if check_auth(request):
        context = {}
        context['groups'] = get_groups(request.user)

        return render_to_response('main_view.html', context, context_instance=RequestContext(request, processors=[custom_proc]))

    else:
        args = {}
        args.update(csrf(request))
        return render_to_response('login.html', args, context_instance=RequestContext(request, processors=[custom_proc]))


def get_groups(user):

    groups = Groups.objects.filter(
        Q(teacher_leader=user) | Q(teacher_follower=user)
    ).values()

    return groups