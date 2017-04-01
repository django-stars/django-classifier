Tutorial
==========

Installation
------------

Simplest way::

  pip install django-classifier

see more at :doc:`install`.


Configuration
-------------

Add :py:mod:`classifier` to ``INSTALLED_APPS`` in your ``setting.py`` file::

  INSTALLED_APPS = (
      'django.contrib.auth',
      # ...
      'classifier',
  )


Set up your models
------------------

You need to create two models for classifier structure and one for data.

First it's basic model without extra data inherited from
:py:class:`~classifier.models.ClassifierAbstract`::

    from classifier.models import ClassifierAbstract

    class ContactClassifier(ClassifierAbstract):
        pass

Second model must contain :py:class:`~django.db.models.fields.ForeignKey` to model
that we created before and inherited from
:py:class:`~classifier.models.ClassifierLabelAbstract`::

    from classifier.models import ClassifierLabelAbstract

    class ContactClassifierLabel(ClassifierLabelAbstract):
        classifier = models.ForeignKey(ContactClassifier, related_name='labels')

Model for data pretty simple in general:
:py:class:`~django.db.models.fields.ForeignKey` to label model
(``ContactClassifierLabel`` in tutorial) and
:py:class:`~django.db.models.fields.CharField` for value::

    from django.conf import settings
    from django.db import models

    class Contact(models.Model):
        user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name='contacts'
        )
        kind = models.ForeignKey(ContactClassifier)
        value = models.CharField(max_length=500)

Then make and run migrations and you are ready to use ``django-classifier``::

    python manage.py makemigrations
    python manage.py migrate


Add some data to classifier models
----------------------------------

Lets add some data to ``ContactClassifier`` and ``ContactClassifierLabel``::

    contact_classifier1 = ContactClassifier.objects.create(
        kind='phone',
        value_type=ContactClassifier.TYPES.STRING,
        value_validator=r'^\+\d{12}$',
        only_one_required=False,
    )
    contact_classifier1.labels.create(label='Mobile')
    contact_classifier1.labels.create(label='Work')
    contact_classifier1.labels.create(label='Home')

    contact_classifier2 = ContactClassifier.objects.create(
        kind='im',
        value_type=ContactClassifier.TYPES.STRING,
        value_validator=None,
        only_one_required=False,
    )
    contact_classifier2.labels.create(label='Skype')
    contact_classifier2.labels.create(label='Jabber')


Create form for validation
--------------------------

To validate values based on classifier record, for this ``django-classifier``
has :py:class:`~classifier.forms.ClassifierFormMixin`::

    from django import forms
    from classifier.forms import ClassifierFormMixin
    from .models import Contact

    class ContactForm(ClassifierFormMixin, forms.ModelForm):
        CLASSIFIER_VALUE_FIELD = 'value'

        class Meta:
            model = Contact
            fields = ('user', 'kind', 'value', )

You have to specify
:py:attr:`~classifier.forms.ClassifierFormMixin.CLASSIFIER_VALUE_FIELD`
attribute to identify name of value field to attach validation based on
classifier record.


Playing with formset
--------------------

:py:mod:`classifier` provide own ``FormSet`` class
:py:class:`~classifier.formsets.ClassifierFormSet` that will add extra forms
for mandatory records and validate if all of them are filled in::

    from django.contrib.auth import get_user_model
    from django.forms import modelformset_factory
    from classifier.formsets import ClassifierFormSet
    from .forms import UserForm, ContactForm
    from .models import Contact

    ContactFormSet = modelformset_factory(
        Contact,
        formset=ClassifierFormSet,
        form=ContactForm
    )

    user = get_user_model().objects.create('login', 'password')
    contact_formset = ContactFormSet(queryset=user.contacts.all())

    print(len(contact_formset.forms))
    print(contact_formset.forms[0].initial)

For now any of classifier records are not marked as required and formset has
only one blank forms as default in Django.

But if you will mark both classifiers as
:py:attr:`~classifier.models.ClassifierAbstract.only_one_required` you will have
two forms with prepopulated labels (*first available label*)::

    ContactClassifier.objects.all().update(only_one_required=True)

    contact_formset = ContactFormSet(queryset=user.contacts.all())
    print(len(contact_formset.forms))
    print(contact_formset.forms[0].initial)
    print(contact_formset.forms[1].initial)

If you will mark all labels as
:py:attr:`~classifier.models.ClassifierLabelAbstract.required` then you will
have 5 forms by default and all of them will be required::

    ContactClassifier.objects.all().update(only_one_required=False)
    ContactClassifierLabel.objects.all().update(required=True)

    contact_formset = ContactFormSet(queryset=user.contacts.all())
    print(len(contact_formset.forms))
