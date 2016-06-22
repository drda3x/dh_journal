# -*- coding:utf-8 -*-
# Модуль для хранения низкоуровневых процедур
# типа: "удалить уроки", "создать абонемент" и тд.

#todo перенести все функции которые могут использоваться в нескольких функциях модуля api сюда

from django.db.models import Model as django_models_class
from application.models import Lessons

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
        fields = []

        for field_name in dir(model):
            try:
                fields.append( (field_name, getattr(model, field_name)) )
            except AttributeError:
                continue

        #fields = map(lambda name: (name, getattr(model, name)), dir(model))
        for field in fields:
            try:
                name = field[0]
                obj = field[1]
                if obj.field.related and obj.field.related_model == fk_class:
                    result.append((name, model))

            except Exception:
                pass

    return result


# Удалить заданное кол-во уроков у заданной группы и заданного студента
def delete_lessons(group, student, date, count):

    passes = set()
    to_delete = []

    for lesson in Lessons.objects.filter(
            group_id=group,
            student_id=student,
            date__gte=date).order_by('date')[:count]:

        passes.add(lesson.group_pass)
        to_delete.append(lesson)

    i_passes = iter(passes)

    while count > 0:
        try:
            current_pass = i_passes.next()

            # Если удаляемые занятия не относятся к мультикарте
            if current_pass.one_group_pass:
                current_count = len(Lessons.objects.filter(group_pass=current_pass))

                if current_count <= count:
                    current_pass.delete()
                    count -= current_count
                else:
                    current_pass.lessons -= (count if current_pass.lessons >= count else 0)
                    current_pass.lessons_origin -= (count if current_pass.lessons >= count else 0)
                    count = 0
                    current_pass.save()

            # Если относятся
            else:
                current_count = len(filter(lambda x: x.group_pass == current_pass, to_delete))
                current_pass.lessons = current_pass.lessons_origin - (
                Lessons.objects.filter(group_pass=current_pass).count() - current_count)
                current_pass.save()

        except StopIteration:
            break

        for l in to_delete:
            try:
                l.delete()
            except AssertionError:
                pass

    return [
        {
            'pid': p.id,
            'cnt': p.lessons
        } for p in passes
    ]
