# -*- coding:utf-8 -*-

from django import forms
from application.models import Groups, WEEK, PassTypes


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
            raise ValueError(
                self.error_messages['required'], code='required'
            )

        # Validate that each value in the value list is in self.choices.
        for val in value.split(','):
            if not self.valid_value(val):
                raise ValueError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )

    def prepare_value(self, value):
        """ Convert the string of comma separated integers in list"""
        return value


class GroupsForm(forms.ModelForm):

    _days = CommaSeparatedSelectInteger(label='Дни', choices=WEEK, widget=forms.CheckboxSelectMultiple())
    _available_passes = CommaSeparatedSelectInteger(label='Абонементы', choices=((i.id, str(i)) for i in PassTypes.objects.all().exclude(one_group_pass=False).order_by('sequence')), widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Groups
        fields = ['name', 'start_date', 'teacher_leader', 'teacher_follower', 'dance_hall', 'is_opened', 'is_settable']