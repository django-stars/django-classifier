from setuptools import setup, find_packages

from classifier import VERSION


def get_readme():
    f = open('README.rst', 'r')
    readme = f.read()
    f.close()

    return readme

setup(
    name='django-classifier',
    version='.'.join(map(str, VERSION)),
    description=(
        'Flexible constructor to create dynamic list of heterogeneous '
        'properties for some kind of entity. This set of helpers useful to '
        'create properties like contacts or attributes for describe '
        'car/computer/etc.'
    ),
    long_description=get_readme(),
    author='Vadym Zakovinko',
    author_email='vadym.zakovinko@djangostars.com',
    url='http://github.com/djangostars/djnago-classifier/',
    packages=find_packages(exclude=['testapp']),
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
    ],
    include_package_data=False,
    zip_safe=False
)
