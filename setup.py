from setuptools import setup, find_packages

import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name="bcqt",
    version="0.1.0",
    description="Boulder Cryogenic Quantum Testbed",
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_dir={'': 'bcqt_hub'},
    packages=find_packages(where='bcqt_hub'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)