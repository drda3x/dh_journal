# -*- coding:utf-8 -*-

from django.utils.functional import cached_property

from django import forms
from django.core.exceptions import ValidationError
from application.models import Groups, WEEK, PassTypes, BonusClasses


class CommaSeparatedSelectInteger(forms.MultipleChoiceField):

    def to_python(self, value):
        if not value:
            return ''

        elif not isinstance(value, (list, tuple)):
            raise ValueError(
                self.error_messages['invalid_list'], code='invalid_list'
            )

        return ','.join(str(val) for val in value)

    def validate(self, value):
        """
        Validates that the input is a string of integers separeted by comma.
        """
        if self.required and not value:
            raise ValidationError(
                self.error_messages['required'], code='required'
            )

        # Validate that each value in the value list is in self.choices.
        for val in value.split(','):
            if not self.valid_value(val):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )

    def prepare_value(self, value):
        """ Convert the string of comma separated integers in list"""
        return value


class CommaSeparatedSelectIntegerWithUpdate(CommaSeparatedSelectInteger):

    def __init__(self, *args, **kwargs):
        super(CommaSeparatedSelectIntegerWithUpdate, self).__init__(*args, **kwargs)

    def refresh_choices(self):
        self.choices = ((i.id, unicode(i)) for i in PassTypes.objects.filter(one_group_pass=True).order_by('sequence'))

    def prepare_value(self, value):
        self.refresh_choices()
        return value.split(',') if value and hasattr(value, 'split') else value


# При выполненнии syncdb код падал ибо не находил таблицу PassTypes
# заменим класс в случае если не найдем таблицу
try:
    class GroupsForm(forms.ModelForm):

        _days = CommaSeparatedSelectInteger(label=u'Дни', choices=WEEK, widget=forms.CheckboxSelectMultiple())
        _available_passes = CommaSeparatedSelectIntegerWithUpdate(label=u'Абонементы', choices=((i.id, str(i)) for i in PassTypes.objects.filter(one_group_pass=True).order_by('sequence')), widget=forms.CheckboxSelectMultiple())

        class Meta:
            model = Groups
            fields = ['name', 'start_date', 'time', 'end_date', 'teacher_leader', 'teacher_follower', 'dance_hall', 'is_opened', 'is_settable']

except Exception:
        class GroupsForm(forms.ModelForm):

            _days = CommaSeparatedSelectInteger(label='Дни', choices=WEEK, widget=forms.CheckboxSelectMultiple())
            _available_passes = None

            class Meta:
                model = Groups
                fields = ['name', 'start_date', 'time', 'end_date', 'teacher_leader', 'teacher_follower', 'dance_hall', 'is_opened', 'is_settable']


try:
    class BonusClassesForm(forms.ModelForm):

        _available_passes = CommaSeparatedSelectIntegerWithUpdate(
            label=u'Абонементы',
            choices=((i.id, str(i)) for i in PassTypes.objects.filter(one_group_pass=True).order_by('sequence')),
            widget=forms.CheckboxSelectMultiple()
        )

        class Meta:
            model = BonusClasses
            fields = ['date', 'time', 'teacher_leader', 'teacher_follower', 'hall', 'can_edit']

except Exception:
        class BonusClassesForm(forms.ModelForm):

            _available_passes = None

            class Meta:
                model = BonusClasses
                fields = ['date', 'time', 'teacher_leader', 'teacher_follower', 'hall', 'can_edit']
