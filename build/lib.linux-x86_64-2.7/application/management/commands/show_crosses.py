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
                    elem1 = elem['o']
                    elem2 = prev_elem['o']

                    if flag:
                        print '%s student: %s  group: %s %s - %s' % (elem1.date, elem1.student.last_name, elem1.group.name, elem1.group.teacher_leader, elem1.group.teacher_follower)
                        print '%s | %s | %s' % (elem2.group_pass.pass_type.name, elem2.group_pass.start_date, elem2.status)

                        flag = False

                    print '%s | %s | %s' % (elem1.group_pass.pass_type.name, elem1.group_pass.start_date, elem1.status)

                else:
                    flag = True

                prev_elem = elem
                elem = iterator.next()

        except StopIteration:
            if not has_crosses:
                print 'No crosses'

            return