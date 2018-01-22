# -*- coding:utf-8 -*-

from copy import deepcopy
from application.models import GroupList, Students
from application.utils.phones import check_phone
from application.system_api import get_models

__all__ = (
	'add_student'
)


def add_student(group_id, student_main_data, e_mail=None, is_org=False, group_list_orm=GroupList): #first_name, last_name,  phone
    """
    :param group_id: Int
    :param student_main_data: tuple (first_name, last_name,  phone) or instance of application.models.Students
    :param e_mail: str
    :param is_org: bool
    :param group_list_orm: GroupList.__class__
    :return: bool
    """

    try:
        if isinstance(student_main_data, Students):
            student = student_main_data
        else:
            first_name, last_name, phone = (lambda x: (x[0].replace(' ', ''), x[1].replace(' ', ''), check_phone(x[2])))(student_main_data)

            try:
                student = Students.objects.get(first_name=first_name, last_name=last_name, phone=phone)
                e_mail = e_mail.replace(' ', '') if e_mail else None
                group_id = int(group_id)
                is_org = is_org == u'true'

            except Students.DoesNotExist:
                student = Students(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    e_mail=e_mail,
                    org=is_org == u'true'
                )

                student.save()

            except Students.MultipleObjectsReturned:
                student = Students.objects.filter(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone
                ).first()
                edit_student(student.pk, student.phone, student.first_name, student.last_name, student.e_mail, student.org)

        group_id = int(group_id)

        try:
            group_list = group_list_orm.objects.get(student=student, group_id=group_id)

        except group_list_orm.DoesNotExist:
            group_list = None

        if not group_list:
            group_list = group_list_orm(
                student=student,
                group_id=group_id
            )
            group_list.save()

        elif not group_list.active:
            group_list.active = True
            group_list.save()

        else:
            return None

        return student.__json__()

    except Exception:
        from traceback import format_exc
        print format_exc()
        return None


def remove_student(group_id, students, group_list_orm):
    try:
        group_list_orm.objects.filter(group__id=group_id, student__id__in=students).select_related('student').update(active=False)
        return True
    except Exception:
        from traceback import format_exc; print format_exc()
        return False


def edit_student(stid, phone, first_name, last_name, e_mail=u'', is_org=False):
    #todo При изменении данных ученика нужно проверить их уникальность.
    #todo если окажется что данные не уникальны - нужно переписать все данные об абонементах,
    #todo посещениях и вообще всем где есть student на один id-шник.

    #todo comments
    #todo debts
    #todo grouplist
    #todo lessons
    #todo passes

    #todo нужно создать пред-деплойный скрипт, который пройдет по всем моделям приложения
    #todo и сделает список моделей у которых есть поле "студент" дабы не заниматься этим при обреботке запроса

    try:

        student = Students.objects.get(pk=stid)
        phone = check_phone(phone)
        first_name = first_name.replace(' ', '')
        last_name = last_name.replace(' ', '')

        if not phone:
            raise TypeError('Phone must be a number')

        # Проверить наличие такого же тлефона
        try:
            same_phone_people = Students.objects.filter(phone=phone).exclude(pk=student.id)
            change_list = []
            errors = []

            for human in same_phone_people:

                # Если есть совпадение по имени, фамилии и номеру телефона - добавляем запись в список на изменение
                if human.first_name.lower() == first_name.lower() and human.last_name.lower() == last_name.lower():
                    change_list.append(human)

                else:
                    errors.append(human)

            # В списке на изменение что-то есть - проходим по всем моделям у которых есть ForeinKey на Students и
            # меняем записи для собранного change_list'a
            if change_list:
                models = get_models(Students)

                for human in change_list:
                    human_backup = deepcopy(human)
                    back_up = []  # список для сохранения предыдущих состояний базы.

                    try:
                        for model in models:
                            cls = model[1]
                            field_name = model[0]
                            params = {field_name: human}
                            records = cls.objects.filter(**params)

                            for record in records:
                                back_up.append(deepcopy(record))
                                setattr(record, field_name, student)
                                record.save()

                        human.delete()

                    except Exception:
                        # Если одно из сохранений провалилось - восстанавливаем предыдущее состояние
                        # для всех записей конкретного человека
                        for record in back_up:
                            record.save()

                        human_backup.save()

            # В списке людей с одинаковыми именами и телефонами что-то есть.
            # выдаем информацию об этимх записях
            if errors:
                pass

        # Совпадений нет
        except Students.DoesNotExist:
            pass

        student.first_name = first_name
        student.last_name = last_name
        student.phone = phone
        student.e_mail = e_mail
        student.org = is_org
        student.save()

        return student.__json__()

    except Exception:
        from traceback import format_exc; print format_exc()
        return False


class Student(object):
    u"""
    Класс для работы с учениками клуба
    Поддерживает:
        1. Добавление/удаление/изменение ученика из системы
        2. Добавление/удаление/изменение групп, долгов и коментариев для конкретного ученика
    """

    def __init__(self, _id=None, first_name=None, last_name=None, phone=None, ):
        pass
