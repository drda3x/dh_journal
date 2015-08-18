# -*- coding: utf-8 -*-

import datetime, copy
from application.models import PassTypes, Passes, Groups, Lessons, Students

from django.db.models import Min, Max, Q


ORG_PASS_HTML_CLASS = 'pass_type_org'
ORG_PASS_HTML_VAL = '#1e90ff'


def get_color_classes():
    u"""
        Получить список классов с цветами типов абонементов
        + спец класс для орг-абонемента
    """

    passes_types = PassTypes.objects.all().order_by('name').values_list('color', flat=True)

    return map(
        lambda i, t: ('pass_type%d' % i, t),
        xrange(0, len(passes_types)),
        passes_types
    ) + [(ORG_PASS_HTML_CLASS, ORG_PASS_HTML_VAL)]


class BasePass(object):

    orm_object = None
    new_pass = False

    def __init__(self, obj):
        self.orm_object = obj

    def check_date(self, date):
        max_date = Lessons.objects.filter(group_pass=self.orm_object).aggregate(Max('date'))
        return self.orm_object.start_date <= date.date() <= max_date['date__max']

    def check_lessons_count(self):
        self.orm_object.lessons = len(Lessons.objects.filter(group_pass=self.orm_object, status=Lessons.STATUSES['not_processed']))
        self.orm_object.save()

    def check_moved_lessons(self):
        count = len(Lessons.objects.filter(student=self.orm_object.student, group_pass=self.orm_object))
        moved = len(Lessons.objects.filter(student=self.orm_object.student, group_pass=self.orm_object, status=Lessons.STATUSES['moved']))
        if self.orm_object.lessons_origin < count - moved:
            map(lambda l: l.delete(), Lessons.objects.filter(student=self.orm_object.student, group_pass=self.orm_object).order_by('date')[:count - self.orm_object.lessons_origin + moved].reverse())
            self.orm_object.skips = self.orm_object.skips_origin - moved
            self.orm_object.save()

    def check_pass_crossing(self, date):
        group = self.orm_object.group
        student = self.orm_object.student
        try:
            # Проверяем пересечения с другими абонементами.
            # Если они есть, то запустить эту функцию для первого занятия этого абонемента.
            crossed_lesson = Lessons.objects.get(date=date, group=group, student=student)
            crossed_pass = crossed_lesson.group_pass
            crossed_pass_lessons = Lessons.objects.filter(date__gte=date, group_pass=crossed_pass)
            mb_new_date = group.get_calendar(len(crossed_pass_lessons)+1, date)[-1]

            wrapped = PassLogic.wrap(crossed_pass)
            wrapped.check_pass_crossing(mb_new_date)
            crossed_lesson.date = mb_new_date
            crossed_lesson.save()

        except Lessons.DoesNotExist:
            # Пересечений с уроками нет, можно переносить
            pass

    def process_lesson(self, date, status):
        lesson = Lessons.objects.get(
            date=date.date(),
            group_pass=self.orm_object
        )

        checker = lambda _x: _x in (Lessons.STATUSES['moved'], Lessons.STATUSES['not_attended'])
        prev_status = lesson.status

        if prev_status == status or all([checker(x) for x in [prev_status, status]]):
            return

        lesson.status = status
        lesson.save()

        if prev_status == Lessons.STATUSES['moved'] and status == Lessons.STATUSES['attended']:
            try:
                lesson = Lessons.objects.filter(group_pass=self.orm_object, status=Lessons.STATUSES['not_attended']).order_by('date')[0]
                lesson.status = Lessons.STATUSES['moved']
                lesson.save()
            except IndexError:
                pass
        elif status == Lessons.STATUSES['moved']:
            last_lesson = Lessons.objects.filter(group_pass=self.orm_object).order_by('date').last()
            new_date = self.orm_object.group.get_calendar(2, last_lesson.date)[-1]

            self.check_pass_crossing(new_date)
            self.create_lessons(new_date, 1)
            self.orm_object.skips -= 1
            self.orm_object.save()

        # elif not all([checker(x) for x in [prev_status, status]]):
        #     self.orm_object.lessons -= 1
        #     self.orm_object.save()

    # Урок посещен
    def set_lesson_attended(self, date, person=None, **kwargs):
        self.process_lesson(date, Lessons.STATUSES['attended'])
        self.check_moved_lessons()
        self.check_lessons_count()

    def write_off(self):
        try:
            lessons = Lessons.objects.filter(group_pass=self.orm_object, status=Lessons.STATUSES['not_processed'])

            for lesson in lessons:
                lesson.status = Lessons.STATUSES['written_off']
                lesson.save()

            self.orm_object.lessons = 0
            self.orm_object.skips = 0
            self.orm_object.save()
            return True

        except Exception:
            return False

    # Урок не посещен
    def set_lesson_not_attended(self, date):
        pass

    # Заморозить
    def freeze(self, date_from, date_to):

        def move_lesson(lesson, new_date):
            lesson.date = new_date
            lesson.save()

        self.orm_object.frozen_date = date_to
        lessons = Lessons.objects.filter(group_pass=self.orm_object, date__gte=date_from, status=Lessons.STATUSES['not_processed']).order_by('date')
        cal = self.orm_object.group.get_calendar(len(lessons), date_to)
        map(move_lesson, lessons, cal)

        self.orm_object.save()

    def cancel_lesson(self, date):

        self.orm_object.frozen_date = date
        lessons = Lessons.objects.filter(group_pass=self.orm_object, date__gte=date).order_by('date')
        first_lesson = lessons.first()

        first_lesson.date = self.orm_object.group.get_calendar(len(lessons), date)[-1]
        first_lesson.status = Lessons.STATUSES['not_processed']
        first_lesson.save()
        self.orm_object.save()

        self.check_moved_lessons()

    def restore_lesson(self, date):
        lesson = Lessons.objects.filter(group_pass=self.orm_object, date__gte=date, status=Lessons.STATUSES['not_processed']).order_by('date').last()

        if lesson:
            lesson.date = date
            lesson.save()

    # Разморозить
    def unfreeze(self, date):
        pass

    # Сменить владельца
    def change_owner(self, new_owner, date=None):

        try:
            new_owner = Students.objects.get(pk=new_owner)
            group = self.orm_object.group

            new_pass = Passes.objects.filter(student=new_owner, lessons__gt=0, group=group).order_by('start_date').last()
            if not new_pass:
                new_pass = Passes(student=new_owner, group=group, pass_type=self.orm_object.pass_type, skips=self.orm_object.skips, lessons=self.orm_object.lessons, start_date=group.last_lesson)
                new_pass.save()
                next_lesson_date = new_pass.start_date
            else:
                last_lesson_date = Lessons.objects.filter(group_pass=new_pass).order_by('date').last()
                next_lesson_date = group.get_calendar(2, last_lesson_date.date)[-1]

            wrapped = PassLogic.wrap(new_pass)
            wrapped.create_lessons(next_lesson_date, self.orm_object.lessons)

            for lesson in Lessons.objects.filter(group_pass=self.orm_object, status=Lessons.STATUSES['not_processed']):
                lesson.delete()

            return True

        except Exception, e:
            from traceback import format_exc
            print format_exc()
            return False

    # Получить календарь
    def get_calendar(self):
        pass

    def create_lessons(self, date, count=None, **kwargs):

        group = kwargs.get('group', None) or self.orm_object.group
        _count = count if count else self.orm_object.lessons
        res = []

        def get_cal(dt, cnt, st=0):
            cl = group.get_calendar(date_from=dt, count=cnt, clean=False)[st:]
            canceled = filter(lambda x: x['canceled'], cl)
            if len(canceled) == 0:
                return cl
            else:
                cleaned = filter(lambda x: not x['canceled'], cl)
                return cleaned + get_cal(
                    canceled[-1]['date'] if canceled[-1]['date'] > cleaned[-1]['date'] else cleaned[-1]['date'],
                    len(canceled) + 1,
                    1
                )

        for _date in group.get_calendar(date_from=date, count=_count):
            lesson = Lessons(
                date=_date,
                group=group,
                student=self.orm_object.student,
                group_pass=self.orm_object,
                status=Lessons.STATUSES['not_processed']
            )

            res.append(lesson)

            lesson.save()

        return res

    def delete(self):
        try:
            for l in Lessons.objects.filter(group_pass=self.orm_object):
                l.delete()

            self.orm_object.delete()
            return True

        except Lessons.DoesNotExist:

            self.orm_object.delete()
            return True

        except Exception:
            return False


class RegularPass(BasePass):
    u"""
    Обычный абонемент
    """

    # Урок не посещен
    def set_lesson_not_attended(self, date):
        status = Lessons.STATUSES['moved'] if self.orm_object.skips and self.orm_object.skips > 0 else Lessons.STATUSES['not_attended']
        self.process_lesson(date, status)
        self.check_lessons_count()


class OrgPass(BasePass):
    u"""
    ОРГ-абонемент
    """

    HTML_CLASS = ORG_PASS_HTML_CLASS
    HTML_VAL = '#1e90ff'

    def set_lesson_not_attended(self, date):
        self.process_lesson(date, Lessons.STATUSES['moved'])
        self.check_lessons_count()

    def check_moved_lessons(self):
        lessons = Lessons.objects.filter(group_pass=self.orm_object).exclude(status=Lessons.STATUSES['moved']).order_by('date')

        delta = len(lessons) - self.orm_object.lessons_origin
        if delta > 0:
            map(lambda l: l.delete(), lessons.reverse()[:delta])


class MultiPass(BasePass):
    u"""
    Мультикарта
    """

    def set_lesson_attended(self, date, person=None, **kwargs):

        try:
            kwargs['group'] = Groups.objects.get(pk=kwargs['group']) if isinstance(kwargs['group'], int) else kwargs['group']

        except Exception:
            raise TypeError('Expected group or group.id in kwargs')

        wright_type = lambda x: x.date() if isinstance(x, datetime.datetime) else x
        if not wright_type(self.orm_object.start_date) <= wright_type(date) <= wright_type(self.orm_object.end_date):
            return

        if not Lessons.objects.filter(group_pass=self.orm_object, date=date).exists():
            lessons = super(MultiPass, self).create_lessons(date, 1, **kwargs)

            for lesson in lessons:
                lesson.status = Lessons.STATUSES['attended']
                lesson.save()

            self.orm_object.lessons -= 1
            self.orm_object.save()

    def create_lessons(self, date, count=None, **kwargs):
        pass


class PassLogic(object):

    @classmethod
    def wrap(cls, obj):

        u"""
        Добавить экземпляру абонемента определенную логику
        """
        if not isinstance(obj, Passes):
            raise TypeError('Pass has to be an instance of Passes!!!!')

        pass_type = obj.pass_type

        # Определяем и возвращаем тип абонемента
        if not pass_type.one_group_pass:
            obj.group = None
            obj.end_date = datetime.date(
                obj.start_date.year if obj.start_date.month < 12 else obj.start_date.year + 1,
                obj.start_date.month + 1 if obj.start_date.month < 12 else 1,
                obj.start_date.day
            )
            obj.save()
            return MultiPass(obj)

        elif obj.student.org:
            return OrgPass(obj)

        else:
            return RegularPass(obj)