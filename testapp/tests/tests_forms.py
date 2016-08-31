import six
from django.test import TestCase
from classifier.exceptions import (
    NoValueFieldNameSpecified, ClassifierLabelModelNotFound
)

from testapp.models import ContactClassifier, ContactClassifierLabel
from testapp.tests.factories import (
    UserFactory, ContactClassifierFactory, ContactClassifierLabelFactory
)
from testapp.forms import ContactForm, UserForm



class ClassifierFormUtilsTest(TestCase):

    def test_get_classifier_label_fieldname(self):
        form = ContactForm()
        self.assertEqual(form.classifier_label_fieldname, 'kind')

    def test_get_classifier_label_model(self):
        form = ContactForm()
        self.assertEqual(form.classifier_label_model, ContactClassifierLabel)


class ClassifierFormValidateRequiredTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_label_required(self):
        label = ContactClassifierLabelFactory(required=True)
        form = ContactForm({
            'user': self.user.pk,
            'kind': label.pk,
            'value': None,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('value', form.errors)
        self.assertEqual(
            form.errors['value'],
            [six.text_type(form.fields['value'].error_messages['required'])]
        )


class ClassifierFormValidateTypeTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        classifier = ContactClassifierFactory(
            value_type=ContactClassifier.TYPES.INT
        )
        self.label = ContactClassifierLabelFactory(classifier=classifier)

    def test_validate_type(self):
        form = ContactForm({
            'user': self.user.pk,
            'kind': self.label.pk,
            'value': 'abc',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('value', form.errors)
        self.assertEqual(
            form.errors['value'],
            [six.text_type(form.error_messages['wrong_type'])]
        )

    def test_validate_type_ok(self):
        form = ContactForm({
            'user': self.user.pk,
            'kind': self.label.pk,
            'value': '1234',
        })

        self.assertTrue(form.is_valid())


class ClassifierFormValidateRegexTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        classifier = ContactClassifierFactory(
            value_validator=r'\+\d{5}'
        )
        self.label = ContactClassifierLabelFactory(classifier=classifier)

    def test_validate_type(self):
        form = ContactForm({
            'user': self.user.pk,
            'kind': self.label.pk,
            'value': '01234567890',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('value', form.errors)
        self.assertEqual(
            form.errors['value'],
            [six.text_type(form.error_messages['wrong_value_format'])]
        )

    def test_validate_type_ok(self):
        form = ContactForm({
            'user': self.user.pk,
            'kind': self.label.pk,
            'value': '+01234567890',
        })

        self.assertTrue(form.is_valid())


class ClassifierWrongFormTest(TestCase):

    def test_no_classifier_value_field_attr(self):
        self.assertRaises(NoValueFieldNameSpecified, UserForm)

    def test_no_label_relation(self):
        UserForm.CLASSIFIER_VALUE_FIELD = 'first_name'
        form = UserForm()

        with self.assertRaises(ClassifierLabelModelNotFound):
            form.classifier_label_fieldname
