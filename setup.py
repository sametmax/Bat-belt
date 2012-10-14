
from setuptools import setup, find_packages

open('MANIFEST.in', 'w').write('\n'.join((
    "include *.md",
)))

setup(

    name="batbelt",
    version="0.1",
    packages=find_packages('.'),
    author="Sam et Max",
    author_email="lesametlemax@gmail.com",
    description="A collection of gagdets make Python even more powerful.",
    long_description=open('README.md').read(),
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

