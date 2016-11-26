#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from application.models import Groups, PassTypes


class Command(BaseCommand):

    def handle(self, *args, **options):
        for group in Groups.objects.all():
            if group.teacher_leader:
                group.teachers.add(group.teacher_leader)

            if group.teacher_follower:
                group.teachers.add(group.teacher_follower)

            for pt in map(int, group._available_passes.split(',') if group._available_passes else []):
                group.available_passes.add(PassTypes.objects.get(pk=pt))

            for pt in map(int, group._external_passes.split(',') if group._external_passes else []):
                group.external_passes.add(PassTypes.objects.get(pk=pt))

            group.save()