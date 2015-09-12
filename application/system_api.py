# -*- coding:utf-8 -*-

from django.db.models import Model as django_models_class


def get_models(fk_class):
    u'''
    Получить список моделей у которых есть оперделенный ForeinKey
    :param fk_class: models.Model
    :return: list
    '''

    result = []  # список кортежей типа: ("имя поля", "класс модели")

    from application import models as app_models

    models = filter(
        lambda obj: obj.__class__ == django_models_class.__class__ and obj != fk_class,
        map(lambda name: getattr(app_models, name), dir(app_models))
    )

    for model in models:
        fields = map(lambda name: (name, getattr(model, name)), dir(model))
        for field in fields:
            try:
                name = field[0]
                obj = field[1]
                if obj.field.related and obj.field.related_model == fk_class:
                    result.append((name, model))

            except Exception:
                pass

    return result


'''
from application.system_api import check_models
check_models()
'''
def check_models():
    from application.models import Students
    print get_models(Students)
