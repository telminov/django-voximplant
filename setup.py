# coding: utf-8
# python setup.py sdist register upload
from distutils.core import setup

setup(
    name='django-voximplant',
    version='0.0.1',
    description='Django application for VoxImplant integration.',
    author='Telminov Sergey',
    url='https://github.com/telminov/django-voximplant',
    packages=[
        'voximplant',
        'voximplant/management',
        'voximplant/management/commands',
        'voximplant/migrations',
    ],
    license='The MIT License',
    install_requires=[
        'django',
        'requests',
    ],
)
