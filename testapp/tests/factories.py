import factory
from django.contrib.auth import get_user_model

from testapp.models import (
    ContactClassifier, ContactClassifierLabel,
    PropertyClassifier, PropertyClassifierLabel
)


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = get_user_model()


class ContactClassifierFactory(factory.django.DjangoModelFactory):
    kind = 'phone'
    value_type = ContactClassifier.TYPES.STRING
    only_one_required = False

    class Meta:
        model = ContactClassifier


class ContactClassifierLabelFactory(factory.django.DjangoModelFactory):
    classifier = factory.SubFactory(ContactClassifierFactory)
    label = factory.Iterator(['Mobile', 'Home', 'Work'])
    required = False

    class Meta:
        model = ContactClassifierLabel


class PropertyClassifierFactory(factory.django.DjangoModelFactory):
    kind = 'hardware'
    value_type = ContactClassifier.TYPES.STRING
    only_one_required = False

    class Meta:
        model = PropertyClassifier


class PropertyClassifierLabelFactory(factory.django.DjangoModelFactory):
    kind = factory.SubFactory(ContactClassifierFactory)
    label = factory.Iterator(['CPU', 'RAM', 'HDD'])
    required = False

    class Meta:
        model = PropertyClassifierLabel
