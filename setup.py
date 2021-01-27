"""Miroslava setup

See https://github.com/kaamiki/miroslava for more help.

"""

from setuptools import find_packages, setup

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers for the
# complete list of available classifiers.
classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

dependencies = []

setup(
    name="miroslava",
    version="1.0.0.dev1",
    description="A simple sandbox environment",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kaamiki/miroslava",
    author="XAMES3",
    author_email="xames3.developer@gmail.com",
    license="MIT",
    classifiers=classifiers,
    keywords="python, miroslava, kaamiki",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6,<4",
    install_requires=dependencies,
    extras_require={
        "dev": [
            "autopep8",
            "black",
            "check-manifest",
            "pytest",
            "pytest-cov",
            "tox",
            "twine",
        ],
        "test": ["coverage", "pytest", "pytest-cov", "tox"],
    },
    project_urls={
        "Source": "https://github.com/kaamiki/miroslava",
        "Bug Reports": "https://github.com/kaamiki/miroslava/issues",
    },
)
