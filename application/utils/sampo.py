#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from pytz import UTC, timezone
from project.settings import TIME_ZONE
from django.utils.timezone import make_aware
from django.db.models import Sum
from application.models import SampoPayments, SampoPasses, SampoPassUsage, HtmlPaymentsTypes, Log


def get_sampo_details(date):

    time_zone = timezone(TIME_ZONE)

    day_begin = date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    begin_time = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_time = (begin_time + datetime.timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(microseconds=1)

    if date.tzinfo is None:
        day_begin = make_aware(day_begin, time_zone)
        day_end = make_aware(day_end, time_zone)
        begin_time = make_aware(begin_time, time_zone)
        end_time = make_aware(end_time, time_zone)

    sampo_passes = SampoPasses.objects.select_related('payment')\
        .filter(payment__date__range=[begin_time, end_time])\
        .exclude(payment__date__gt=datetime.datetime.combine(date.date(), datetime.datetime.max.time()))

    today_payments = SampoPayments.objects.filter(date__range=(day_begin, day_end)).order_by('pk')

    totals = {
        'add': today_payments.filter(money__gt=0).aggregate(Sum('money')).get('money__sum') or 0,
        'write_off': abs(today_payments.filter(money__lt=0).aggregate(Sum('money')).get('money__sum') or 0)
    }

    totals['delta'] = totals['add'] - totals['write_off']

    pass_buffer = []

    for payment in today_payments:
        _pass = filter(lambda p: p.payment.id == payment.id, sampo_passes)
        if _pass:
            pass_buffer.append(int(_pass[0].id))
            payment.sampo_pass = _pass[0]

    pass_usages = SampoPassUsage.objects.select_related('sampo_pass').filter(date__range=(day_begin, day_end)).order_by('pk')
    today_bought = []

    def get_data(elem):
        if isinstance(elem, SampoPayments):
            result = dict(
                id='p' + str(elem.pk),
                type=HtmlPaymentsTypes.ADD if elem.money >= 0 else HtmlPaymentsTypes.WRITE_OFF,
                payment='+%d' % elem.money if elem.money > 0 else elem.money,
            )

            if hasattr(elem, 'sampo_pass'):
                result['comment'] = '%s %s - %s' % (elem.sampo_pass.surname, elem.sampo_pass.name, u'абон.')
                today_bought.append(elem.sampo_pass.id)
            elif elem.comment:
                result['comment'] = elem.comment

            return result
        else:
            return dict(
                id='u' + str(elem.sampo_pass.pk),
                type=HtmlPaymentsTypes.DEFAULT,
                payment='%s %s' % (elem.sampo_pass.surname, elem.sampo_pass.name)
            )

    today_payments = [
        {
            'date': i.date.astimezone(timezone(TIME_ZONE)).strftime('%H:%M'),
            'info': get_data(i)
        }
        for i in list(pass_usages.exclude(sampo_pass_id__in=pass_buffer)) + list(today_payments)
    ]

    if today_payments:
        today_payments.sort(key=lambda x: x['date'])
        today_payments.reverse()

    passes = map(
        lambda x: setattr(
            x,
            'used_today',
            x.id in pass_usages.values_list('sampo_pass_id', flat=True) or x.id in today_bought
        ) or x,
        sampo_passes
    )

    return passes, today_payments, totals


def write_log(msg):
    Log(msg=msg).save()
