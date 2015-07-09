from setuptools import setup

setup(
    name='audos',
    version='0.1-dev',
    description='Sync sound with its recording',
    url='https://github.com/banteg/audos',
    author='banteg',
    author_email='banteeg@gmail.com',

    modules=['audos'],

    entry_points={
        'console_scripts': [
            'audos = audos:main',
        ],
    }
)
