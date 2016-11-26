# -*- coding:utf-8 -*-

from django.core.management.base import BaseCommand
from application.models import Lessons, Passes, CanceledLessons


class Command(BaseCommand):

    def handle(self, *args, **options):
        Lessons.objects.all().delete()
        Passes.objects.all().delete()
        CanceledLessons.objects.all().delete()
        print 'OK'