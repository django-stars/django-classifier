from datetime import date, datetime
from django.test import TestCase
from classifier.exceptions import ClassifierModelNotFound

from testapp.models import (
    ContactClassifier, ContactClassifierLabel,
    PropertyClassifier, PropertyClassifierLabel,
    MagicClassifierLabel
)
from testapp.tests.factories import (
    ContactClassifierFactory, ContactClassifierLabelFactory,
    PropertyClassifierFactory, PropertyClassifierLabelFactory
)


class ClassifierToIntTest(TestCase):

    def setUp(self):
        self.classifier = ContactClassifier.objects.create(
            kind='test',
            value_type=ContactClassifier.TYPES.INT
        )

    def test_int(self):
        self.assertEqual(self.classifier.to_python('11'), 11)

    def test_float(self):
        self.assertRaises(ValueError, self.classifier.to_python, '11.1')

    def test_string(self):
        self.assertRaises(ValueError, self.classifier.to_python, 'abc')


class ClassifierToFloatTest(TestCase):

    def setUp(self):
        self.classifier = ContactClassifier.objects.create(
            kind='test',
            value_type=ContactClassifier.TYPES.FLOAT
        )

    def test_int(self):
        self.assertEqual(self.classifier.to_python('11'), 11.)

    def test_float(self):
        self.assertEqual(self.classifier.to_python('11.1'), 11.1)

    def test_string(self):
        self.assertRaises(ValueError, self.classifier.to_python, 'abc')


class ClassifierToBooleanTest(TestCase):

    def setUp(self):
        self.classifier = ContactClassifier.objects.create(
            kind='test',
            value_type=ContactClassifier.TYPES.BOOLEAN
        )

    def test_checkbox(self):
        self.assertEqual(self.classifier.to_python('on'), True)

    def test_empty(self):
        self.assertEqual(self.classifier.to_python(''), False)

    def test_string(self):
        self.assertRaises(ValueError, self.classifier.to_python, 'abc')


class ClassifierToDateTest(TestCase):

    def setUp(self):
        self.classifier = ContactClassifier.objects.create(
            kind='test',
            value_type=ContactClassifier.TYPES.DATE
        )

    def test_date(self):
        self.assertEqual(
            self.classifier.to_python('2016-08-29'),
            date(2016, 8, 29)
        )

    def test_string(self):
        self.assertRaises(ValueError, self.classifier.to_python, 'abc')


class ClassifierToDateTimeTest(TestCase):

    def setUp(self):
        self.classifier = ContactClassifier.objects.create(
            kind='test',
            value_type=ContactClassifier.TYPES.DATETIME
        )

    def test_datetime(self):
        self.assertEqual(
            self.classifier.to_python('2016-08-29 10:13:29'),
            datetime(2016, 8, 29, 10, 13, 29)
        )

    def test_string(self):
        self.assertRaises(ValueError, self.classifier.to_python, 'abc')


class ClassifierLabelRelationMethodsTest(TestCase):

    def test_with_related_name_get_classifier_model(self):
        self.assertEqual(
            ContactClassifierLabel.get_classifier_model(),
            ContactClassifier
        )

    def test_with_related_name_get_classifier_related_field(self):
        self.assertEqual(
            ContactClassifierLabel.get_classifier_related_field().name,
            'classifier'
        )

    def test_with_related_name_get_classifier_instance(self):
        classifier = ContactClassifierFactory()
        label = ContactClassifierLabelFactory(classifier=classifier)

        self.assertEqual(label.get_classifier_instance(), classifier)

    def test_without_related_name_get_classifier_model(self):
        self.assertEqual(
            PropertyClassifierLabel.get_classifier_model(),
            PropertyClassifier
        )

    def test_without_related_name_get_classifier_related_field(self):
        self.assertEqual(
            PropertyClassifierLabel.get_classifier_related_field().name,
            'kind'
        )

    def test_without_related_name_get_classifier_instance(self):
        classifier = PropertyClassifierFactory()
        label = PropertyClassifierLabelFactory(kind=classifier)

        self.assertEqual(label.get_classifier_instance(), classifier)

    def test_no_relation_from_label_to_classifier(self):
        self.assertRaises(
            ClassifierModelNotFound,
            MagicClassifierLabel.get_classifier_model
        )
