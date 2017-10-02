"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# To use a consistent encoding
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
long_description = "LexPredict LexNLP: Information retrievla and extraction for real, unstructured legal text."

setup(
    name='lexnlp',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1.1',

    description='LexPredict LexNLP',
    long_description=long_description,

    # The project's main homepage.
    url='https://lexnlp.com',

    # Author details
    author='ContraxSuite, LLC',
    author_email='support@contraxsuite.com',

    # Choose your license
    license='AGPL',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Legal Industry',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
        'Topic :: Office/Business',
        'Topic :: Text Processing :: Linguistic',
    ],

    # What does your project relate to?
    keywords='legal contract document analytics nlp ml machine learning natural language',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['*tests*']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    # py_modules=['lexnlp'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        # 'datefinder==0.6.1',
        'nltk==3.2.4',
        'num2words==0.5.5',
        'pandas==0.20.3',
        'regex==2016.1.10',
        'reporters-db==1.0.12.1',
        'scikit-learn==0.19.0',
        'scipy==0.19.1'
    ],
    # dependency_links=[
    #     'https://github.com/LexPredict/datefinder/archive/master.zip#egg=datefinder-0.6.1'
    # ],

    # Install any data files from packages.
    # The data files must be specified via the distutils’ MANIFEST.in file.
    include_package_data=True,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['pytest>=2.8.5', 'mock', 'pytz>=2015.7'],
    #    'test': ['pytest>=2.8.5', 'mock', 'pytz>=2015.7'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
