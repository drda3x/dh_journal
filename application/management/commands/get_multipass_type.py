#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from application.models import PassTypes


class Command(BaseCommand):

    def handle(self, *args, **options):
        for p in PassTypes.objects.filter(one_group_pass=False):
            print '%d - %s' % (p.id, p.name)