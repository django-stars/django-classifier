from django import forms
from django.contrib.auth import get_user_model

from classifier.forms import ClassifierFormMixin

from .models import Contact


class ContactForm(ClassifierFormMixin, forms.ModelForm):
    CLASSIFIER_VALUE_FIELD = 'value'

    class Meta:
        model = Contact
        fields = '__all__'


class UserForm(ClassifierFormMixin, forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = '__all__'
