# based on https://github.com/pypa/sampleproject/blob/master/setup.py

import setuptools
from setuptools import setup, find_packages

from codecs import open
from os import path

import glob

read_rst = lambda f: open(f, 'r').read()


setup(
    name='asciidots',

    version='1.0.7',

    description='Interpreter for the AsciiDots esolang.',
    long_description=read_rst('README.rst'),

    url='https://github.com/aaronduino/asciidots',

    author='Aaron Janse',
    author_email='gitduino@gmail.com',

    license='APGL-v3.0',

    python_requires='>=3',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Education',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Topic :: Games/Entertainment',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Software Development :: Interpreters',
        'Operating System :: OS Independent',

        'License :: OSI Approved :: GNU Affero General Public License v3',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='asciidots esolang esoteric ascii dataflow language programming fun',

    packages=['dots'],
    scripts=['interpret.py'],

    package_data={'dots': glob.glob('dots/libs/*.dots')},

    data_files=[
        ('dots', glob.glob('dots/libs/*.dots'))
    ],

    install_requires=['Click'],

    entry_points='''
        [console_scripts]
        asciidots=interpret:main
    ''',
)
