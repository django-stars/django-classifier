Installation
============

Requirements
------------

* Python 2.7, 3.4, 3.5
* Django 1.8, 1.9, 1.10


Official releases
-----------------

Official releases are available from `PyPI`_.

Download the .zip distribution file and unpack it. Inside is a script
named ``setup.py``. Enter this command::

   python setup.py install

...and the package will install automatically.

or just install with help of pip::

   pip install django-classifier


.. _`PyPI`: http://pypi.python.org/pypi/django-classifier/


Development version
-------------------

Alternatively, you can get the latest source from our `git`_ repository::

   git clone http://github.com/django-stars/django-classifier.git django-classifier

Add ``django-classifier/classifier`` folder to `PYTHONPATH`_.

You can verify that the application is available on your PYTHONPATH by opening
a Python interpreter and entering the following commands::

   >> import classifier
   >> classifier.VERSION
   (0, 2)

.. caution::
    The development version may contain bugs which are not present in the
    release version and introduce backwards-incompatible changes.


.. _`git`: http://git-scm.com/
.. _`PYTHONPATH`: http://docs.python.org/tut/node8.html#SECTION008110000000000000000
