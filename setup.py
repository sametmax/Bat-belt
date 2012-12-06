
from setuptools import setup, find_packages

open('MANIFEST.in', 'w').write('\n'.join((
    "include *.rst",
)))

from batbelt import __version__

setup(

    name="batbelt",
    version=__version__,
    packages=find_packages('.'),
    author="Sam et Max",
    author_email="lesametlemax@gmail.com",
    description="A collection of gagdets that makes Python even more powerful.",
    long_description=open('README.rst').read(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: zlib/libpng License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7"
    ],
    url="https://github.com/sametmax/Bat-belt"
)

