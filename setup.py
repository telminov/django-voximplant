# coding: utf-8
# python setup.py sdist register upload
from setuptools import setup, find_packages

setup(
    name='django-voximplant',
    version='0.0.4',
    description='Django application for VoxImplant integration.',
    author='Telminov Sergey',
    author_email='sergey@telminov.ru',
    url='https://github.com/telminov/django-voximplant',
    include_package_data=True,
    packages=find_packages(),
    license='The MIT License',
    requires=[
        'django',
        'requests',
        'pyzmq',
    ],
)
