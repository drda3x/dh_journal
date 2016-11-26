# -*- coding:utf-8 -*-

from django.core.management.base import BaseCommand
from application.models import Passes


class Command(BaseCommand):

    def handle(self, *args, **options):

        for p in Passes.objects.all().select_related():
            p.lessons_origin = p.pass_type.lessons
            p.skips_origin = p.pass_type.skips

            p.save()