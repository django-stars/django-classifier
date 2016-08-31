import six
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.forms import modelformset_factory

from classifier.exceptions import ClassifierLabelModelNotFound
from classifier.formsets import ClassifierFormSet

from testapp.models import ContactClassifierLabel, Contact
from testapp.tests.factories import (
    UserFactory,
    ContactClassifierFactory, ContactClassifierLabelFactory
)


class FormSetRequiredExtraFormsTest(TestCase):

    def setUp(self):
        self.classifier = ContactClassifierFactory()
        self.label_mobile = ContactClassifierLabelFactory(
            classifier=self.classifier,
            label='Mobile'
        )
        self.label_work = ContactClassifierLabelFactory(
            classifier=self.classifier,
            label='Work'
        )

    def test_both_labels_are_required(self):
        ContactClassifierLabel.objects.all().update(required=True)

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        contact_formset = ContactFormSet(
            queryset=Contact.objects.all()
        )

        self.assertEqual(len(contact_formset.forms), 2)
        self.assertIn(
            {'kind': self.label_mobile.pk},
            [f.initial for f in contact_formset.forms],
        )
        self.assertIn(
            {'kind': self.label_work.pk},
            [f.initial for f in contact_formset.forms],
        )

    def test_mobile_is_required(self):
        self.label_mobile.required = True
        self.label_mobile.save()

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        contact_formset = ContactFormSet(
            queryset=Contact.objects.all()
        )

        self.assertEqual(len(contact_formset.forms), 1)
        self.assertIn(
            {'kind': self.label_mobile.pk},
            [f.initial for f in contact_formset.forms],
        )
        self.assertNotIn(
            {'kind': self.label_work.pk},
            [f.initial for f in contact_formset.forms],
        )

    def test_one_of_label_is_required(self):
        self.classifier.only_one_required = True
        self.classifier.save()

        self.assertFalse(
            ContactClassifierLabel.objects.filter(required=True).exists()
        )

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        contact_formset = ContactFormSet(
            queryset=Contact.objects.all()
        )

        self.assertEqual(len(contact_formset.forms), 1)
        self.assertIn(
            {'kind': self.label_mobile.pk},
            [f.initial for f in contact_formset.forms],
        )
        self.assertNotIn(
            {'kind': self.label_work.pk},
            [f.initial for f in contact_formset.forms],
        )


class FormSetInitialTest(TestCase):

    def setUp(self):
        self.classifier = ContactClassifierFactory()
        self.label_mobile = ContactClassifierLabelFactory(
            classifier=self.classifier,
            label='Mobile'
        )
        self.label_work = ContactClassifierLabelFactory(
            classifier=self.classifier,
            label='Work'
        )

    def test_initial_as_dict(self):
        ContactClassifierLabel.objects.all().update(required=True)

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        contact_formset = ContactFormSet(
            queryset=Contact.objects.all(),
            initial={
                'user': 43,
            }
        )

        self.assertEqual(len(contact_formset.forms), 2)
        self.assertIn(
            {'user': 43, 'kind': self.label_mobile.pk},
            [f.initial for f in contact_formset.forms],
        )
        self.assertIn(
            {'user': 43, 'kind': self.label_work.pk},
            [f.initial for f in contact_formset.forms],
        )

    def test_initial_as_list(self):
        ContactClassifierLabel.objects.all().update(required=True)

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        contact_formset = ContactFormSet(
            queryset=Contact.objects.all(),
            initial=[
                {'user': 41},
                {'user': 42},
            ]
        )

        self.assertEqual(len(contact_formset.forms), 2)
        self.assertIn(
            {'user': 41, 'kind': self.label_mobile.pk},
            [f.initial for f in contact_formset.forms],
        )
        self.assertIn(
            {'user': 42, 'kind': self.label_work.pk},
            [f.initial for f in contact_formset.forms],
        )

    def test_initial_not_enough_items_in_list(self):
        ContactClassifierLabel.objects.all().update(required=True)

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        contact_formset = ContactFormSet(
            queryset=Contact.objects.all(),
            initial=[
                {'user': 41},
            ]
        )

        self.assertEqual(len(contact_formset.forms), 2)
        self.assertIn(
            {'user': 41, 'kind': self.label_mobile.pk},
            [f.initial for f in contact_formset.forms],
        )
        self.assertIn(
            {'kind': self.label_work.pk},
            [f.initial for f in contact_formset.forms],
        )

    def test_initial_as_dict_with_default_behaviour(self):
        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        contact_formset = ContactFormSet(
            queryset=Contact.objects.all(),
            initial={'user': 41}
        )

        self.assertEqual(len(contact_formset.forms), 1)
        self.assertIn(
            {'user': 41},
            [f.initial for f in contact_formset.forms],
        )


class FormSetRequiredValidationTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.classifier = ContactClassifierFactory()
        self.label_mobile = ContactClassifierLabelFactory(
            classifier=self.classifier,
            label='Mobile'
        )
        self.label_work = ContactClassifierLabelFactory(
            classifier=self.classifier,
            label='Work'
        )

    def get_management_form(self, total_forms=1):
        return {
            'form-TOTAL_FORMS': total_forms,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }

    def test_one_label_required(self):
        self.label_mobile.required = True
        self.label_mobile.save()

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        data = {}
        data.update(self.get_management_form())
        contact_formset = ContactFormSet(data, queryset=Contact.objects.all())

        self.assertFalse(contact_formset.is_valid())
        self.assertEqual(len(contact_formset.non_form_errors()), 1)
        self.assertIn(
            six.text_type(self.label_mobile),
            contact_formset.non_form_errors()[0]
        )

    def test_two_labels_required(self):
        ContactClassifierLabel.objects.all().update(required=True)

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        data = {}
        data.update(self.get_management_form(2))
        contact_formset = ContactFormSet(data, queryset=Contact.objects.all())

        self.assertFalse(contact_formset.is_valid())
        self.assertEqual(len(contact_formset.non_form_errors()), 1)
        labels = [self.label_mobile, self.label_work]
        error_msg = contact_formset.non_form_errors()[0]
        self.assertTrue(any([
            ', '.join(map(six.text_type, labels)) in error_msg,
            ', '.join(map(six.text_type, labels[::-1])) in error_msg,
        ]))

    def test_classifier_required(self):
        self.classifier.only_one_required = True
        self.classifier.save()

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        data = {}
        data.update(self.get_management_form())
        contact_formset = ContactFormSet(data, queryset=Contact.objects.all())

        self.assertFalse(contact_formset.is_valid())
        self.assertEqual(len(contact_formset.non_form_errors()), 1)
        self.assertIn(
            '/'.join(map(six.text_type, [self.label_mobile, self.label_work])),
            contact_formset.non_form_errors()[0]
        )

    def test_one_required_label_present(self):
        ContactClassifierLabel.objects.all().update(required=True)

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        data = {
            'form-0-user': self.user.pk,
            'form-0-kind': self.label_mobile.pk,
            'form-0-value': '5555555'
        }
        data.update(self.get_management_form())
        contact_formset = ContactFormSet(data, queryset=Contact.objects.all())

        self.assertFalse(contact_formset.is_valid())
        self.assertEqual(len(contact_formset.non_form_errors()), 1)
        self.assertIn(
            six.text_type(self.label_work),
            contact_formset.non_form_errors()[0]
        )

    def test_one_label_of_required_classifier_present(self):
        self.label_mobile.required = True
        self.label_mobile.save()

        classifier = ContactClassifierFactory(kind='im', only_one_required=True)
        label_jabber = ContactClassifierLabelFactory(
            classifier=classifier,
            label='Jabber'
        )
        label_skype = ContactClassifierLabelFactory(
            classifier=classifier,
            label='Skype'
        )

        ContactFormSet = modelformset_factory(
            Contact,
            formset=ClassifierFormSet,
            fields=('id', 'user', 'kind', 'value', )
        )

        data = {
            'form-0-user': self.user.pk,
            'form-0-kind': label_jabber.pk,
            'form-0-value': 'username'
        }
        data.update(self.get_management_form())
        contact_formset = ContactFormSet(data, queryset=Contact.objects.all())

        self.assertFalse(contact_formset.is_valid())
        self.assertEqual(len(contact_formset.non_form_errors()), 1)
        self.assertIn(
            six.text_type(self.label_mobile),
            contact_formset.non_form_errors()[0]
        )
        self.assertNotIn(
            six.text_type(label_skype),
            contact_formset.non_form_errors()[0]
        )


class FormSetRelationMethodsTest(TestCase):

    def test_no_relation_to_label(self):
        UserModel = get_user_model()

        UserFormSet = modelformset_factory(
            UserModel,
            formset=ClassifierFormSet,
            fields=('id', 'email', )
        )
        self.assertRaises(
            ClassifierLabelModelNotFound,
            UserFormSet,
            queryset=UserModel.objects.all()
        )
