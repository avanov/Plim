import os
import sys

from setuptools import find_packages
from setuptools import setup



PY3K = sys.version_info >= (3,0)
readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='Plim',
    version='0.7.12',
    packages=find_packages(exclude=['tests']),
    # Plim is a preprocessor for Mako template language.
    # But it doesn't depend on the Mako package itself.
    install_requires=[
        'Mako>=0.7.3',
        # We use reStructuredText (docutils' component) for both supporting
        # the "-rest" extension and project documenting. So, ensure that the docutils
        # get installed or upgraded on the target machine
        'docutils>=0.3',
        # We use Markdown for the "-markdown" extension
        'markdown2>=1.4.2',
        # We use CoffeeScript for "-coffee" extension
        'CoffeeScript',
        # We use SCSS for "-scss/sass" extension
        # There is a SyntaxError during pySCSS==1.1.3 installation
        # https://github.com/Kronuz/pyScss/issues/87
        # TODO: remove exact version marker when the issue will be fixed.
        PY3K and 'pyScss==1.1.1' or 'pyScss',
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
            'plimc = plim.console:plim_compiler',
        ]
    },

    # PyPI metadata
    # Read more at http://docs.python.org/distutils/setupscript.html#meta-data
    author="Maxim Avanov",
    author_email="maxim.avanov@gmail.com",
    maintainer="Maxim Avanov",
    maintainer_email="maxim.avanov@gmail.com",
    description="Plim is a Python port of Ruby's Slim template language built on top of the Mako Templates",
    long_description=readme,
    license="MIT",
    url="https://github.com/2nd/Plim",
    download_url="https://github.com/2nd/Plim",
    keywords="mako templates ruby slim jade pyjade pyramid",
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
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Text Processing :: Markup :: HTML',
    ]
)
