# -*- coding: utf-8 -*-

import datetime, copy
from application.models import PassTypes, Passes, Groups, Lessons
from application.utils.lessons import LessonsFactory


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


class AbstractPass(object):

    orm_object = None
    new_pass = False

    def __init__(self, obj):
        self.orm_object = obj

    def check_moved_lessons(self):
        count = len(Lessons.objects.filter(student=self.orm_object.student, group_pass=self.orm_object))
        moved = len(Lessons.objects.filter(student=self.orm_object.student, group_pass=self.orm_object, status=Lessons.STATUSES['moved']))
        if self.orm_object.pass_type.lessons < count - moved:
            Lessons.objects.filter(student=self.orm_object.student, group_pass=self.orm_object).order_by('date').last().delete()
            self.orm_object.skips += 1
            self.orm_object.save()

    def process_lesson(self, date, status):
        lesson = Lessons.objects.get(
            date=date,
            group_pass=self.orm_object
        )

        checker = lambda _x: _x in (Lessons.STATUSES['attended'], Lessons.STATUSES['not_attended'])
        prev_status = lesson.status
        lesson.status = status
        lesson.save()

        if status == Lessons.STATUSES['moved']:
            pt = self.orm_object.pass_type
            new_date = self.orm_object.group.get_calendar(pt.lessons + pt.skips - self.orm_object.skips + 1, self.orm_object.start_date)[-1]
            new_lesson = Lessons(
                date=new_date,
                group=self.orm_object.group,
                student=self.orm_object.student,
                group_pass=self.orm_object,
                status=Lessons.STATUSES['not_processed']
            )
            new_lesson.save()
            self.orm_object.skips -= 1
            self.orm_object.save()

        elif not all([checker(x) for x in [prev_status, status]]):
            self.orm_object.lessons -= 1
            self.orm_object.save()

    # Урок посещен
    def set_lesson_attended(self, date, person=None, **kwargs):
        self.process_lesson(date, Lessons.STATUSES['attended'])
        self.check_moved_lessons()

    # Урок не посещен
    def set_lesson_not_attended(self, date):
        pass

    # Заморозить
    def freeze(self, start_date, stop_date):
        pass

    # Разморозить
    def unfreeze(self, date):
        pass

    # Сменить владельца
    def change_owner(self, new_owner):
        pass

    # Получить календарь
    def get_calendar(self):
        pass

    def create_lessons(self, date):

        for _date in self.orm_object.group.get_calendar(date_from=date, count=self.orm_object.lessons):
            lesson = Lessons(
                date=_date,
                group=self.orm_object.group,
                student=self.orm_object.student,
                group_pass=self.orm_object,
                status=Lessons.STATUSES['not_processed']
            )

            lesson.save()


class RegularPass(AbstractPass):
    u"""
    Обычный абонемент
    """

    # Урок не посещен
    def set_lesson_not_attended(self, date):
        status = Lessons.STATUSES['moved'] if self.orm_object.skips and self.orm_object.skips > 0 else Lessons.STATUSES['not_attended']
        self.process_lesson(date, status)


class OrgPass(AbstractPass):
    u"""
    ОРГ-абонемент
    """

    HTML_CLASS = ORG_PASS_HTML_CLASS
    HTML_VAL = '#1e90ff'

    def set_lesson_not_attended(self, date):
        self.process_lesson(date, Lessons.STATUSES['moved'])


class MultiPass(AbstractPass):
    u"""
    Мультикарта
    """

    def set_lesson_attended(self, date, person=None, **kwargs):

        if not self.orm_object.start_date <= date.date() <= self.orm_object.end_date:
            return

        lesson = Lessons(
            date=date,
            group_id=kwargs['group'],
            student=self.orm_object.student,
            group_pass=self.orm_object,
            status=Lessons.STATUSES['attended']
        )

        lesson.save()
        self.orm_object.lessons -= 1
        self.orm_object.save()

    def create_lessons(self, date):
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
            obj.save()
            obj.end_date = datetime.date(
                obj.start_date.year if obj.start_date.month < 12 else obj.start_date.year + 1,
                obj.start_date.month + 1 if obj.start_date.month < 12 else 1,
                obj.start_date.day
            )
            return MultiPass(obj)

        elif obj.student.org:
            return OrgPass(obj)

        else:
            return RegularPass(obj)

    @classmethod
    def get_or_create(cls, **kwargs):

        if 'id' in kwargs:
            obj = Passes.objects.get(pk=kwargs['id'])
            return cls.wrap(obj)

        else:
            student = kwargs.get('student_id', None)
            group_id = kwargs.get('group_id', None)
            date = kwargs.get('start_date', None)

            if not any([student, group_id, date]):
                raise TypeError('Wrong arguments')

            if 'presence' in kwargs.iterkeys():
                presence = kwargs['presence']
                kwargs.__delitem__('presence')

            else:
                presence = None

            try:
                obj = Passes.objects.get(**kwargs)
                wraped = cls.wrap(obj)

            except Passes.DoesNotExist:
                try:
                    kwargs['pass_type__one_group_pass'] = False
                    kwargs.__delitem__('group_id')

                    obj = Passes.objects.get(**kwargs)
                    wraped = cls.wrap(obj)

                except Passes.DoesNotExist:
                    pt = PassTypes.objects.get(pk=kwargs['pass_type'])
                    group = Groups.objects.get(pk=group_id)


                    obj = Passes(
                        student_id=student,
                        start_date=date.date(),
                        pass_type=pt,
                        lessons=pt.lessons,
                        skips=pt.skips,
                        end_date=kwargs.get('date', None),
                        group=group
                    )
                    obj.save()

                    wraped = cls.wrap(obj)
                    if presence:
                        wraped.presence = presence

                    wraped.new_pass = True

                    wraped.create_lessons(date)

            return wraped