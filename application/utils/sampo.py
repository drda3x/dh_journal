#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from pytz import UTC, timezone
from project.settings import TIME_ZONE
from application.models import SampoPayments, SampoPasses, SampoPassUsage, HtmlPaymentsTypes, Log


def get_sampo_details(date):

    day_begin = date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC)
    day_end = date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=UTC)
    begin_time = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC)
    end_time = (begin_time + datetime.timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(microseconds=1)

    sampo_passes = SampoPasses.objects.select_related('payment')\
        .filter(payment__date__range=[begin_time, end_time])

    today_payments = SampoPayments.objects.filter(date__range=(day_begin, day_end)).order_by('pk')

    pass_buffer = []

    for payment in today_payments:
        _pass = filter(lambda p: p.payment.id == payment.id, sampo_passes)
        if _pass:
            pass_buffer.append(int(_pass[0].id))
            payment.sampo_pass = _pass[0]

    pass_usages = SampoPassUsage.objects.select_related('sampo_pass').filter(date__range=(day_begin, day_end)).order_by('pk')

    def get_data(elem):
        if isinstance(elem, SampoPayments):
            result = dict(
                id='p' + str(elem.pk),
                type=HtmlPaymentsTypes.ADD if elem.money >= 0 else HtmlPaymentsTypes.WRITE_OFF,
                payment='+%d' % elem.money if elem.money > 0 else elem.money,
            )

            if hasattr(elem, 'sampo_pass'):
                result['comment'] = '%s %s - %s' % (elem.sampo_pass.surname, elem.sampo_pass.name, u'абон.')
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
        lambda x: setattr(x, 'used_today', x.id in pass_usages.values_list('sampo_pass_id', flat=True)) or x,
        sampo_passes
    )

    return passes, today_payments


def write_log(msg):
    Log(msg=msg).save()
