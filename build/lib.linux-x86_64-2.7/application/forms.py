# -*- coding:utf-8 -*-

from django.utils.functional import cached_property

from django import forms
from django.core.exceptions import ValidationError
from application.models import Groups, WEEK, PassTypes, BonusClasses
from application.app_admin.app_widgets import ListWidget, DateListField
from django.forms.widgets import TextInput


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

    def __init__(self, qs, *args, **kwargs):
        self.qs = qs
        super(CommaSeparatedSelectIntegerWithUpdate, self).__init__(*args, **kwargs)

    def refresh_choices(self):
        self.choices = ((i.id, unicode(i)) for i in self.qs)

    def prepare_value(self, value):
        self.refresh_choices()
        return value.split(',') if value and hasattr(value, 'split') else value


class GroupsForm(forms.ModelForm):

    _days = CommaSeparatedSelectInteger(label=u'Дни', choices=WEEK, widget=forms.CheckboxSelectMultiple())
    updates = DateListField(widget=ListWidget(), required=False, label=u'Донаборы')

    class Meta:
        model = Groups
        fields = ['name', 'dance', 'level', 'start_date', 'end_date', 'time', 'end_time', 'teachers', 'dance_hall', 'available_passes', 'external_passes', 'is_settable', 'free_placees', 'duration', 'lending_message', 'course_details', 'course_results']


class BonusClassesForm(forms.ModelForm):

    class Meta:
        model = BonusClasses
        fields = ['date', 'time', 'end_time', 'hall', 'teachers', 'available_groups', 'available_passes', 'can_edit']
