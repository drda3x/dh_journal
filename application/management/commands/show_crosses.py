# -*- coding:utf-8 -*-

from django.core.management.base import BaseCommand
from application.models import Lessons, Students, Groups


class Command(BaseCommand):

    def handle(self, *args, **options):

        doubles = [
            {
                'k': (lesson.student, lesson.group, lesson.date),
                'o': lesson
            } for lesson in Lessons.objects.all().order_by('student', 'group', 'date')
        ]

        iterator = iter(doubles)
        has_crosses = False

        try:
            flag = True
            prev_elem = iterator.next()
            elem = iterator.next()

            while 1:
                if elem['k'] == prev_elem['k']:
                    has_crosses = True
                    _elem = elem['o']

                    if flag:
                        print '%s student: %s  group: %s %s - %s' % (_elem.date, _elem.student.last_name, _elem.group.name, _elem.group.teacher_leader, _elem.group.teacher_follower)
                        print prev_elem['o'].status
                        flag = False

                    print _elem.status

                else:
                    flag = True

                prev_elem = elem
                elem = iterator.next()

        except StopIteration:
            if not has_crosses:
                print 'No crosses'

            return