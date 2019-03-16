from setuptools import setup, find_packages
from codecs import open
from os import path

long_description= 'Python library for vesync API to control etekcity US 7A and 15A and European 10A wifi smart outlets (round and rectangular) and in wall wifi smart switches.  See the github page for further documentation: https://github.com/webdjoe/pyvesync_v2'

setup(
    name='pyvesync_v2',
    version='0.9.7',
    description='Python library for vesync API for Etekcity Smart Outlets & switches',
    long_description=long_description,
    url='https://github.com/webdjoe/pyvesync_v2',
    author='Joseph Trabulsy',
    author_email='webdjoe@gmail.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.0',
    ],
    keywords=['iot', 'vesync', 'etekcity', 'smart plug', 'smart switch'],
    packages=find_packages('src'),
    package_dir={'': "src"},
    zip_safe=False,
    install_requires=[
        'requests>=2.20.0',
        'pytz',
        'tzlocal'
    ],
)
