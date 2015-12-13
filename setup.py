from setuptools import setup

setup(
    name='audos',
    version='0.2-dev',
    description='Sync sound with its recording',
    url='https://github.com/banteg/audos',
    author='banteg',
    author_email='banteeg@gmail.com',

    modules=['audos'],
    install_requires=['click'],

    entry_points={
        'console_scripts': [
            'audos = audos:main',
        ],
    }
)
