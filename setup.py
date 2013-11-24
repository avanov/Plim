import io
import os
import sys

from setuptools import find_packages
from setuptools import setup


PY3K = sys.version_info >= (3,0)


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


long_description = read(
    os.path.join(os.path.dirname(__file__), 'README.rst'),
    os.path.join(os.path.dirname(__file__), 'CHANGES'),
)


setup(
    name='Plim',
    version='0.9.1',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'Mako>=0.9.0',
        'babel>=1.3',
        # We use reStructuredText (docutils' component) for both supporting
        # the "-rest" extension and project documenting. So, ensure that the docutils
        # get installed or upgraded on the target machine
        'docutils>=0.3',
        # We use Markdown for the "-markdown" extension
        'markdown2>=1.4.2',
        # We use CoffeeScript for "-coffee" extension
        'CoffeeScript',
        # We use SCSS for "-scss/sass" extension
        'pyScss>=1.2.0.post3',
        # We use the stylus package for "-stylus" extension
        # https://github.com/bkad/python-stylus
        'stylus'
    ],
    setup_requires=['nose>=1.1.2'],
    tests_require=['coverage'],
    package_data={
        # If any package contains *.txt or *.rst files, include them
        '':['*.txt', '*.rst',]
    },
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'plimc = plim.console:plimc',
        ]
    },

    # PyPI metadata
    # Read more at http://docs.python.org/distutils/setupscript.html#meta-data
    author="Maxim Avanov",
    author_email="maxim.avanov@gmail.com",
    maintainer="Maxim Avanov",
    maintainer_email="maxim.avanov@gmail.com",
    description="Plim is a Python port of Ruby's Slim template language built on top of Mako Templates",
    long_description=long_description,
    license="MIT",
    url="https://github.com/avanov/Plim",
    download_url="https://github.com/avanov/Plim",
    keywords="mako templates ruby slim jade pyjade pyramid flask haml pyhaml",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Pylons',
        'Framework :: Pyramid',
        'Framework :: TurboGears',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Text Processing :: Markup :: HTML',
    ]
)
