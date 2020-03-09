# based on https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages

from codecs import open
from os import path

import glob

read_rst = lambda f: open(f, 'r').read()

dots_libs = glob.glob('dots/libs/*.dots')
dots_libs = ['/'.join(path.split('/')[-2:]) for path in dots_libs]

setup(
    name='asciidots',
    version='1.3.4',
    description='Interpreter for the AsciiDots esolang.',
    long_description=read_rst('README.rst'),
    url='https://github.com/aaronduino/asciidots',
    author='Aaron Janse',
    author_email='gitduino@gmail.com',
    license='APGL-v3.0',
    python_requires='>=2.6, <4',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=
    'asciidots esolang esoteric ascii dataflow language programming fun',
    packages=find_packages(),
    package_data={'dots': dots_libs},
    install_requires=['Click'],
    entry_points='''
        [console_scripts]
        asciidots=dots.__main__:main
    ''', )
