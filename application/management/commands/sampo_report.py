#!/usr/bin/env python
# -*- coding: utf-8 -*-


u"""
Комманда для формирования файла-отчета за сампо
"""

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from application.models import SampoPayments, SampoPasses
from django.db.models import Sum
from pytz import timezone


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        tz = timezone("Europe/Moscow")

        print "Enter the date (format: 'mm.yyyy')..."
        inp = str(input()).split('.')
        date = datetime(*reversed(map(int, inp)), day=1, tzinfo=tz)

        mth = date.month
        day = timedelta(days=1)

        while date.month == mth:
            payments = SampoPayments.objects.filter(date__range=[
                datetime.combine(date, datetime.min.time()).replace(tzinfo=tz),
                datetime.combine(date, datetime.max.time()).replace(tzinfo=tz)
            ])

            passes = SampoPasses.objects.select_related('payment').filter(payment__in=payments)

            total = payments.aggregate(total=Sum("money"))
            passes_total = passes.aggregate(total=Sum("payment__money"))
            neg_total = payments.filter(money__lte=0).aggregate(total=Sum("money"))

            print "%s\t%d\t%d\t%d\t" % (
                date.strftime('%d.%m.%Y'),
                total["total"] or 0,
                passes_total['total'] or 0,
                neg_total['total'] or 0
            )

            date += day
