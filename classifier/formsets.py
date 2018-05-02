import six
from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.models import BaseModelFormSet
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from .exceptions import ClassifierLabelModelNotFound
from .models import ClassifierLabelAbstract


class ClassifierFormSet(BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        super(ClassifierFormSet, self).__init__(*args, **kwargs)

        self.add_required_to_extra()

    def add_required_to_extra(self):
        """
        Method create extra forms for required records from classifier
        with selected needed kinds by default.
        """
        def get_form_initial(label, i):
            initial = {
                self.classifier_label_related_fieldname: label.pk,
            }
            if self.initial_extra and isinstance(self.initial_extra, dict):
                initial.update(self.initial_extra)
            elif isinstance(self.initial_extra, (list, tuple)):
                try:
                    _initial = self.initial_extra[i]
                except IndexError:
                    pass
                else:
                    initial.update(_initial)

            return initial

        initial_extra = []
        ClassifierLabelModel = self.classifier_label_model
        ClassifierModel = ClassifierLabelModel.get_classifier_model()

        exists_items = self.get_queryset().values_list(
            self.classifier_label_related_fieldname,
            flat=True
        )

        required_labels = (
            ClassifierLabelModel.objects
            .filter(required=True)
            .exclude(pk__in=exists_items)
        )
        for i, label in enumerate(required_labels):
            initial_extra.append(get_form_initial(label, i))

        required_classifiers = ClassifierModel.objects.filter(
            only_one_required=True
        )

        # Django 1.9+
        # https://docs.djangoproject.com/en/1.9/releases/1.9/#field-rel-changes
        if DJANGO_VERSION[0] == 1 and DJANGO_VERSION[1] < 9:
            related_name = (
                ClassifierLabelModel
                .get_classifier_related_field()
                .rel.get_accessor_name()
            )
        else:
            related_name = (
                ClassifierLabelModel
                .get_classifier_related_field()
                .remote_field.get_accessor_name()
            )

        for i, classifier in enumerate(required_classifiers):
            labels = getattr(classifier, related_name)
            if not labels.filter(pk__in=exists_items).exists():
                initial_extra.append(get_form_initial(labels.first(), i))

        if initial_extra:
            self.initial_extra = initial_extra
        elif isinstance(self.initial_extra, dict):
            self.initial_extra = [self.initial_extra]

        self.extra = max(self.extra, len(initial_extra))

    def clean(self):
        super(ClassifierFormSet, self).clean()
        self.validate_required()

    def validate_required(self):
        """
        Validate if all required records are filled in

        :raises django.core.exceptions.ValidationError: if one or mode records
          are absent
        """
        ClassifierLabelModel = self.classifier_label_model
        label_related = ClassifierLabelModel.get_classifier_related_field().name

        qs = ClassifierLabelModel.objects.filter(
            Q(required=True)
            | Q(**{'{}__only_one_required'.format(ClassifierLabelModel.get_classifier_related_field().name): True})
        )
        for form in self.forms:
            kind = form.cleaned_data.get(
                self.classifier_label_related_fieldname
            )
            if kind and kind.required:
                qs = qs.exclude(pk=kind.pk)
            elif kind and kind.get_classifier_instance().only_one_required:
                labels_ids = (
                    ClassifierLabelModel.objects
                    .filter(**{
                        label_related: kind.get_classifier_instance(),
                    })
                    .values_list('pk', flat=True)
                )
                qs = qs.exclude(pk__in=labels_ids)

        if qs.count() > 0:
            fields = set()
            for label in qs:
                if label.required:
                    fields.add(six.text_type(label))
                elif label.get_classifier_instance().only_one_required:
                    labels = '/'.join(
                        map(
                            six.text_type,
                            ClassifierLabelModel.objects.filter(**{
                                label_related: label.get_classifier_instance(),
                            })
                        )
                    )
                    fields.add(labels)

            msg = _('This data required: {}').format(', '.join(fields))
            raise ValidationError(msg)

    @cached_property
    def classifier_label_related_fieldname(self):
        """
        Return name of field related to model inherited from
        :py:class:`~classifier.models.ClassifierLabelAbstract`.
        """
        for field in self.model._meta.fields:
            if (
                field.related_model
                and issubclass(field.related_model, ClassifierLabelAbstract)
            ):
                return field.name

        raise ClassifierLabelModelNotFound()

    @cached_property
    def classifier_label_model(self):
        """
        Property return model inherited from
        :py:class:`~classifier.models.ClassifierLabelAbstract` and used for
        one of field in model for this formset.

        :return: model inherited from :py:class:`~classifier.models.ClassifierLabelAbstract`
        :raises ClassifierLabelModelNotFound: field can not be found
        """
        for field in self.model._meta.fields:
            if (
                field.related_model
                and issubclass(field.related_model, ClassifierLabelAbstract)
            ):
                return field.related_model

        raise ClassifierLabelModelNotFound()
