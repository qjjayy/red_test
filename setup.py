#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    Auto Red Test
    ~~~~~~~~~~~~~~~~~~~
    Auto Create PyTest Frame and Fake Test Parameters For Red
    :copyright: (c) 2019 by Junjie Qiu
    :license: MIT, see LICENSE for more details
"""
from os import path
from codecs import open
from setuptools import setup

basedir = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(basedir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='auto-red-test',  # 包名称
    version='0.2.0',  # 版本
    url='https://github.com/qjjayy/red_test',
    license='MIT',
    author='Junjie Qiu',
    author_email='xiaohaixie@qq.com',
    description='Auto Create PyTest Frame and Fake Test Parameters For Red',
    long_description=long_description,
    long_description_content_type='text/markdown',  # 长描述内容类型
    platforms='any',
    packages=['auto_red_test'],  # 包含的包列表
    zip_safe=False,
    include_package_data=False,
    install_requires=['pytest', 'pyaml', 'Faker', 'bson', 'dictdiffer'],
    keywords='auto red test',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ]
)
