import setuptools

with open("pypi_description.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysimdb",
    # version will be automatically determined by setuptools-scm
    author="Shayan Heidari",
    author_email="shayanheidari01@gmail.com",
    description="A lightweight, JSON-based database library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shayanheidari01/pysimdb",
    project_urls={
        "Bug Tracker": "https://github.com/shayanheidari01/pysimdb/issues",
        "Documentation": "https://github.com/shayanheidari01/pysimdb#readme",
        "Source Code": "https://github.com/shayanheidari01/pysimdb",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pysimdjson>=5.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
    keywords="database json database-library python-database lightweight-database",
    license="GNU General Public License v3 (GPLv3)",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
)