from setuptools import find_packages
from setuptools import setup



setup(
    name='Plim',
    version='0.7.0',
    packages=find_packages(exclude=['tests']),
    # Plim is a preprocessor for Mako template language.
    # But it doesn't depend on the Mako package itself.
    install_requires=[
        # We use reStructuredText (docutils' component) for both supporting
        # the "-rest" extension and project documenting. So, ensure that the docutils
        # get installed or upgraded on the target machine
        'docutils>=0.3',
        # We use Markdown for the "-markdown" extension
        'markdown2>=1.4.2',
        # We use CoffeeScript for "-coffee" extension
        'CoffeeScript',
        # We use SCSS for "-scss/sass" extension
        'pyScss'
    ],
    setup_requires=['nose>=1.1.2'],
    tests_require=['coverage'],
    package_data={
        # If any package contains *.txt or *.rst files, include them
        '':['*.txt', '*.rst',]
    },

    # PyPI metadata
    # Read more at http://docs.python.org/distutils/setupscript.html#meta-data
    author="Maxim Avanov",
    author_email="maxim.avanov@gmail.com",
    maintainer="Maxim Avanov",
    maintainer_email="maxim.avanov@gmail.com",
    description="Plim is a Python port of Ruby's Slim template language built on top of the Mako Templates",
    long_description=open('README.rst').read(),
    license="MIT",
    url="https://github.com/2nd/Plim",
    download_url="https://github.com/2nd/Plim",
    keywords="mako templates ruby slim jade pyjade",
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