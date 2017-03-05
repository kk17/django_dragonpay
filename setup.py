from setuptools import setup

setup(
    name='django_dragonpay',
    version='0.1',
    description='DragonPay plugin for Django',
    author='Ivan Dominic Baguio',
    author_email='baguio.ivan@gmail.com',
    packages=['django_dragonpay'],
    install_requires=[
        'requests==2.11.1',
        'Django==1.10.4',
        'lxml==3.7.3',
    ]
)

__author__ = 'Ivan Dominic Baguio'
