from setuptools import setup

setup(
    name='pablo',
    version='0.1.0',
    description='automatic sketching of plunderphonic songs',
    url='https://github.com/ftzeng/pablo',
    author='Francis Tseng',
    author_email='f@frnsys.com',
    license='MIT',

    packages=['pablo'],
    install_requires=[
        'click',
        'pydub',
        'lxml',
        'requests',
        'youtube_dl'
    ],
    entry_points='''
        [console_scripts]
        pablo=pablo:cli
    ''',
)