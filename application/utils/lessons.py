#! /usr/bin/env python
# -*- coding: utf-8 -*-

from application.models import Lessons


class Lesson(object):
    status = None
    rus = None

    def __init__(self, lesson=None, **kwargs):
        self.orm_object = lesson if lesson else Lessons(**kwargs)
        self.orm_object.status = self.status

    def save(self):
        self.orm_object.save()

    @property
    def can_skip(self):
        return self.orm_object.group_pass.skips > 0

    @property
    def student(self):
        return self.orm_object.student

    @property
    def group_pass(self):
        return self.orm_object.group_pass

    def skip(self):
        if not self.orm_object.student.org:
            self.orm_object.group_pass.skips -= 1
            self.orm_object.group_pass.save()
        self.change_type(MovedLesson)

    def set_attended(self):
        self.change_type(AttendedLesson)
        self.reduce_lessons_count()

    def set_not_attended(self):
        self.change_type(NotAttendedLesson)
        self.reduce_lessons_count()

    def reduce_lessons_count(self):
        self.orm_object.group_pass.lessons -= 1
        self.orm_object.group_pass.save()



    @property
    def date(self):
        return self.orm_object.date

    def change_type(self, new_type):
        orm_object = self.orm_object
        new_type_class = LessonsFactory.create(new_type, lesson=orm_object)
        self.__class__ = new_type_class.__class__
        self.__dict__.clear()
        self.__dict__.update(new_type_class.__dict__)
        self.save()


class NotProcessedLesson(Lesson):
    status = Lessons.STATUSES['not_processed']
    rus = Lessons.STATUSES_RUS['not_processed']


class AttendedLesson(Lesson):
    status = Lessons.STATUSES['attended']
    rus = Lessons.STATUSES_RUS['attended']


class NotAttendedLesson(Lesson):
    status = Lessons.STATUSES['not_attended']
    rus = Lessons.STATUSES_RUS['not_attended']


class MovedLesson(Lesson):
    status = Lessons.STATUSES['moved']
    rus = Lessons.STATUSES_RUS['moved']


class FrozenLesson(Lesson):
    status = Lessons.STATUSES['frozen']
    rus = Lessons.STATUSES_RUS['frozen']


class LessonsFactory(object):
    pass
    # lessons_types = {
    #     'not_processed': NotProcessedLesson,
    #     'attended': AttendedLesson,
    #     'not_attended': NotAttendedLesson,
    #     'moved': MovedLesson,
    #     'frozen': FrozenLesson
    # }
    #
    # @classmethod
    # def get(cls, t=None, **kwargs):
    #
    #     if t:
    #         kwargs['status'] = cls.lessons_types[t].status if isinstance(t, str) else t.status
    #
    #     qs = Lessons.objects.filter(**kwargs)
    #     types = {val: key for key, val in Lessons.STATUSES.iteritems()}
    #     try:
    #         result = []
    #         for i in qs:
    #             t = types[i.status]
    #             result.append(cls.lessons_types[t](i))
    #
    #         return result
    #
    #     except Lessons.DoesNotExist:
    #         return []
    #
    # @classmethod
    # def get_phantom_lesson(cls, t='not_processed', **kwargs):
    #     lesson = Lessons(**kwargs)
    #     return cls.lessons_types[t](lesson)
    #
    # @classmethod
    # def create(cls, _type, **kwargs):
    #     if _type in cls.lessons_types.itervalues():
    #         return _type(**kwargs)
    #     try:
    #         return cls.lessons_types[_type](**kwargs)
    #     except KeyError:
    #         raise TypeError('Wrong type of the lesson class')