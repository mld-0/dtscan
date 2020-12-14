
from distutils.core import setup
from setuptools import setup

test_depend = [ 
    'pytest'
    'pandas'
    'tzlocal'
    'pytz'
]

setup(name="dtscan",
    version="0.2",
    author="Matthew Davis",
    author_email="mld.0@protonmail.com",
    description="Scan for, process, and analyse datetimes in text",
    packages = ['dtscan', 'tests'],
    tests_require=test_depend,
    entry_points={
        'console_scripts': [
            'dtscan= dtscan.__main__:cliscan',
        ],
    }
)




