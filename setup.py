"""Miroslava setup

See https://github.com/kaamiki/miroslava for more help.

"""

from setuptools import find_packages, setup

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers for the
# complete list of available classifiers.
classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
]

dev_dependencies = [
    "black",
    "flake8",
    "mypy",
]

test_dependencies = [
    "pytest",
    "tox",
]

setup(
    name="miroslava",
    version="1.0.0",
    author="XAMES3",
    author_email="xames3.developer@gmail.com",
    url="https://github.com/kaamiki/miroslava",
    description="A simple sandbox environment",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    keywords="python, miroslava, kaamiki",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    extras_require={
        "dev": dev_dependencies,
        "test": test_dependencies,
    },
    project_urls={
        "Source": "https://github.com/kaamiki/miroslava",
        "Tracker": "https://github.com/kaamiki/miroslava/issues",
    },
    zip_safe=False,
)
