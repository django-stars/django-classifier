import re
from django import forms
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from .exceptions import ClassifierLabelModelNotFound, NoValueFieldNameSpecified
from .models import ClassifierLabelAbstract


class ClassifierFormMixin(object):
    """
    Formset form mixin to enable validation for value connected to classifier.
    """

    CLASSIFIER_VALUE_FIELD = None
    """Name of field for value used in relation with classifier"""

    error_messages = {
        'wrong_type': _('Wrong type of value'),
        'wrong_value_format': _('Wrong value format'),
    }

    def __init__(self, *args, **kwargs):
        super(ClassifierFormMixin, self).__init__(*args, **kwargs)
        self.setup_value_validators()

    @cached_property
    def classifier_label_model(self):
        """
        :return: end model inherited from
          :py:class:`~classifier.models.ClassifierLabelAbstract` used in
          current form
        :raises ClassifierLabelModelNotFound: if related field wasn't found
        """
        fieldname = self.classifier_label_fieldname

        return self.fields[fieldname].queryset.model

    @cached_property
    def classifier_label_fieldname(self):
        """
        :return: Return name of field that is relation to end model inherited from
          :py:class:`~classifier.models.ClassifierLabelAbstract`
        :raises ClassifierLabelModelNotFound: if field can not be found
        """
        for fieldname in self.fields:
            field = self.fields[fieldname]
            if (
                hasattr(field, 'queryset')
                and issubclass(field.queryset.model, ClassifierLabelAbstract)
            ):
                return fieldname

        raise ClassifierLabelModelNotFound(
            '"{}" doesn\'t have field that related to model inherited '
            'from ClassifierLabelAbstract'.format(self.__class__.__name__)
        )

    def setup_value_validators(self):
        """
        Attach validator for value field specified in
        :py:attr:`~ClassifierFormMixin.CLASSIFIER_VALUE_FIELD`

        :raises NoValueFieldNameSpecified: if
          :py:attr:`~ClassifierFormMixin.CLASSIFIER_VALUE_FIELD` is blank
        """
        if not self.CLASSIFIER_VALUE_FIELD:
            raise NoValueFieldNameSpecified(
                'CLASSIFIER_VALUE_FIELD should containce name of value field'
            )

        setattr(
            self,
            'clean_{}'.format(self.CLASSIFIER_VALUE_FIELD),
            self.validate_value_field
        )

    def validate_value_field(self):
        """
        Validate value based on classifier record.

        Will be attathed to right field by call
        :py:meth:`~ClassifierFormMixin.setup_value_validators`
        in :py:meth:`~ClassifierFormMixin.__init__`
        """
        classifier_label = self.cleaned_data[self.classifier_label_fieldname]
        classifier = classifier_label.get_classifier_instance()
        value = self.cleaned_data[self.CLASSIFIER_VALUE_FIELD]

        if (
            value
            and classifier.value_validator
            and not re.match(classifier.value_validator, value)
        ):
            raise forms.ValidationError(
                self.error_messages['wrong_value_format']
            )

        if value:
            try:
                value = classifier.to_python(value)
            except ValueError:
                raise forms.ValidationError(
                    self.error_messages['wrong_type']
                )

        return value
