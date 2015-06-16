# -*- coding: utf-8 -*-

from application.models import PassTypes


def get_color_classes():
    u"""
        Получить список классов с цветами типов абонементов
    """

    passes_types = PassTypes.objects.all().order_by('name').values_list('color')

    return map(
        lambda i, t: ('pass_type%d' % i, t[0]),
        xrange(0, len(passes_types)),
        passes_types
    )