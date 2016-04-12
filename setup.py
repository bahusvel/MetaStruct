from setuptools import setup

setup(
    name='cor',
    version='0.1',
    py_modules=['mstruct', 'ms_compiler'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        mstruct=mstruct:mstruct
    ''',
)