import six
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.translation import ugettext_lazy as _

from .exceptions import ClassifierModelNotFound


@python_2_unicode_compatible
class ClassifierAbstract(models.Model):
    """
    Base class to create classifier models. Will provide base data and functions
    like validation and ``to_python`` (convert from string to real type).

    In simplest case should be created model just inherited from this abstract
    model without extra code.

    ``kind`` - custom identificator for classifier type (like: phone)
    ``value_type`` - expected type of value (like: string)
    ``value_validator`` - regex to validate extered value (like: \+\d{12})
    ``only_one_required`` - checkmark to make one on available lables required

    Supported types: ``int``, ``float``, ``string``, ``boolean``, ``date``,
    ``datatime``.

    Labels with kind give posibility to create one type of record with
    different names, like kind is `phone` and available lables are
    "Mobile", "Home", "Work" etc.
    """

    class TYPES:
        INT = 'int'
        FLOAT = 'float'
        STRING = 'str'
        BOOLEAN = 'bool'
        DATE = 'date'
        DATETIME = 'datetime'

        ALL = (
            (INT, _('Integer')),
            (FLOAT, _('Float')),
            (STRING, _('String')),
            (BOOLEAN, _('Boolean')),
            (DATE, _('Date')),
            (DATETIME, _('Date time')),
        )

    kind = models.CharField(max_length=200, unique=True, verbose_name=_('Kind'))
    """custom identificator for classifier type (like: phone)"""
    value_type = models.CharField(
        max_length=20,
        choices=TYPES.ALL,
        verbose_name=_('Type of value')
    )
    """expected type of value (like: string)"""
    value_validator = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_('Value validator'),
        help_text=_('Regex to validate value')
    )
    """regex to validate extered value (like: \+\d{12})"""
    only_one_required = models.BooleanField(
        default=False,
        verbose_name=_('only one of available labels is required')
    )
    """checkmark to make one on available lables required"""

    class Meta:
        abstract = True

    def __str__(self):
        return self.kind

    def to_python(self, value):
        """
        run convertor from string to type in ``value_type`` field
        """
        cleaner = getattr(self, 'to_python_{}'.format(self.value_type))
        return cleaner(value)

    @staticmethod
    def to_python_int(value):
        return int(value)

    @staticmethod
    def to_python_float(value):
        return float(value)

    @staticmethod
    def to_python_str(value):
        return six.text_type(value)

    @staticmethod
    def to_python_bool(value):
        if value.lower() in ['on', 'yes', 'true']:
            return True
        elif value:
            raise ValueError('Can\'t convert "{}" to boolean'.format(value))

        return False

    @staticmethod
    def to_python_date(value):
        date = parse_date(value)
        if value and not date:
            raise ValueError('Can\'t convert "{}" to date'.format(value))

        return date

    @staticmethod
    def to_python_datetime(value):
        datetime = parse_datetime(value)
        if value and not datetime:
            raise ValueError('Can\'t convert "{}" to datetime'.format(value))

        return datetime


@python_2_unicode_compatible
class ClassifierLabelAbstract(models.Model):
    """
    Base model class to define several human readable names for each
    classifier kind.
    """
    label = models.CharField(max_length=200, verbose_name=_('Label'))
    """human redable label for data"""
    required = models.BooleanField(default=False, verbose_name=_('required'))
    """checkmark to make label required"""

    class Meta:
        abstract = True

    def __str__(self):
        return self.label

    def get_classifier_instance(self):
        """
        :return: instance of related classifier
        """
        return getattr(self, self.get_classifier_related_field().name)

    @classmethod
    def get_classifier_related_field(cls):
        """
        :return: field related to model inherited from ClassifierAbstract.
        :raises ClassifierModelNotFound: if related field wasn't found

        .. caution::
            not field name
        """
        for field in cls._meta.fields:
            if (
                field.related_model
                and issubclass(field.related_model, ClassifierAbstract)
            ):
                return field

        raise ClassifierModelNotFound(
            '"{}" doesn\'t have relation to model inherited from "{}"'.format(
                cls.__name__,
                ClassifierAbstract.__name__
            )
        )

    @classmethod
    def get_classifier_model(cls):
        """
        :return: related model inherited from ClassifierAbstract
        """
        return cls.get_classifier_related_field().related_model
