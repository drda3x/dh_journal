#! /usr/bin/env python
# -*- coding: utf-8 -*-

from application.models import Lessons


class NotProcessedLesson(Lessons):
    pass


class AttendedLesson(Lessons):
    pass


class NotAttendedLesson(Lessons):
    pass


class MovedLesson(Lessons):
    pass


class FrozenLesson(Lessons):
    pass