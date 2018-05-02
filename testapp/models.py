from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from classifier.models import ClassifierAbstract, ClassifierLabelAbstract


@python_2_unicode_compatible
class Contact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='contacts',
        on_delete=models.CASCADE
    )
    kind = models.ForeignKey('ContactClassifierLabel', on_delete=models.CASCADE)
    value = models.CharField(max_length=200)

    def __str__(self):
        return '{}: {}'.format(self.kind, self.value)


# Contact - right structure with related_name in label
class ContactClassifier(ClassifierAbstract):
    pass


class ContactClassifierLabel(ClassifierLabelAbstract):
    classifier = models.ForeignKey(
        ContactClassifier,
        related_name='labels',
        on_delete=models.CASCADE
    )


# Property - right structure without related_name in label
class PropertyClassifier(ClassifierAbstract):
    pass


class PropertyClassifierLabel(ClassifierLabelAbstract):
    kind = models.ForeignKey(PropertyClassifier, on_delete=models.CASCADE)


# Magic - wrong structure, no ForeignKey from label to classifier
class MagicClassifier(ClassifierAbstract):
    pass


class MagicClassifierLabel(ClassifierLabelAbstract):
    pass
