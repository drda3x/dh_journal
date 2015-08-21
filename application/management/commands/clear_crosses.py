# -*- coding:utf-8 -*-

from django.core.management.base import BaseCommand
from application.models import Lessons, Students, Groups
from application.utils.groups import get_group_students_list


class Command(BaseCommand):

    def handle(self, *args, **options):

        for group in Groups.objects.all():
            for student in get_group_students_list(group):
                cashe = []

                for lesson in Lessons.objects.filter(group=group, student=student):
                    if lesson.date in cashe:
                        lesson.delete()
                    else:
                        cashe.append(lesson.date)

        print 'OK'