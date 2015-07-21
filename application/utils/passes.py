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

    def __init__(self, obj):
        self.orm_object = obj

    def process_lesson(self, date, status):
        lesson = Lessons.objects.get(
            date=date,
            group_pass=self.orm_object
        )
        lesson.status = status
        lesson.save()

        if status == Lessons.STATUSES['moved']:
            new_date = self.orm_object.group.get_calendar(self.orm_object.lessons+1, date)[-1]
            new_lesson = Lessons(
                date=new_date,
                group=self.orm_object.group,
                student=self.orm_object.student,
                group_pass=self.orm_object,
                status=Lessons.STATUSES['not_processed']
            )
            new_lesson.save()

    # Урок посещен
    def set_lesson_attended(self, date, person=None):
        self.process_lesson(date, Lessons.STATUSES['attended'])
        self.orm_object.lessons -= 1
        self.orm_object.save()

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
        if self.orm_object.skips and self.orm_object.skips > 0:
            self.process_lesson(date, Lessons.STATUSES['moved'])
            self.orm_object.skips -= 1
            self.orm_object.save()
        else:
            self.process_lesson(date, Lessons.STATUSES['not_attended'])
            self.orm_object.lessons -= 1
            self.orm_object.save()


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

    def set_lesson_attended(self, date, person=None):

        if date > self.orm_object.start_date + datetime.timedelta(days=self.orm_object.pass_type.deadline):
            return

        lesson = Lessons(
            date=date,
            group=self.orm_object.group,
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
        if not pass_type.one_group_pass and obj.end_date:
            obj.group = None
            obj.save()
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

            try:
                obj = Passes.objects.get(**kwargs)
                wraped = cls.wrap(obj)
#student__id=student, group__id=group_id, start_date=date.date()
            except Passes.DoesNotExist:

                pt = PassTypes.objects.get(pk=kwargs['pass_type'])
                group = Groups.objects.get(pk=group_id)

                obj = Passes(
                    student_id=student,
                    start_date=date,
                    pass_type=pt,
                    lessons=pt.lessons,
                    skips=pt.skips,
                    end_date=kwargs.get('date', None),
                    group=group
                )
                obj.save()

                wraped = cls.wrap(obj)
                wraped.create_lessons(date)

            return wraped