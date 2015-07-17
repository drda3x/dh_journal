# -*- coding: utf-8 -*-

import datetime
from application.models import PassTypes, Passes, Groups
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

    abstract = True

    orm_object = None

    def __init__(self, obj):
        self.orm_object = obj

    # Обработать урок
    def process_lesson(self, date, person=None):
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


class RegularPass(AbstractPass):
    u"""
    Обычный абонемент
    """
    pass


class OrgPass(AbstractPass):
    u"""
    ОРГ-абонемент
    """

    HTML_CLASS = ORG_PASS_HTML_CLASS
    HTML_VAL = '#1e90ff'


class MultiPass(AbstractPass):
    u"""
    Мультикарта
    """
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
        if pass_type.multi_pass and not pass_type.skips and pass_type.deadline:
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
            date = kwargs.get('date', None)

            if not any([student, group_id, date]):
                raise TypeError('Wrong arguments')

            try:
                obj = Passes.objects.filter(student__id=student, group__id=group_id, start_date=date.date())
                return cls.wrap(obj)

            except Passes.DoesNotExist:

                pt = PassTypes.objects.get(pk=kwargs['pass_type_id'])
                group = Groups.objects.get(pk=group_id)

                obj = Passes(
                    student_id=student,
                    start_date=date,
                    pass_type=pt,
                    lessons=pt.lessons,
                    skips=pt.skips
                )

                obj.save()

                obj.group.add(group)

                for lessons_date in group.get_calendar(date_from=date, count=obj.lessons):
                    LessonsFactory.create(
                        'not_processed',
                        date=lessons_date,
                        group=group,
                        student_id=student,
                        group_pass=pt,
                    ).save()

                return cls.wrap(obj)