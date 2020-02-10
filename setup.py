import setuptools

from oapispec.version import VERSION

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='oapispec',
    version=VERSION,
    author='Ray Epps',
    author_email='rayharryepps@gmail.com',
    description='A library of decorators and functions for generating open api specs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rayepps/oapispec',
    packages=[
        'oapispec',
        'oapispec.core'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3',
    install_requires=[
        'aniso8601',
        'attrs',
        'importlib-metadata',
        'jsonschema',
        'more-itertools',
        'pyrsistent',
        'pytz',
        'six',
        'Werkzeug'
    ]
)
