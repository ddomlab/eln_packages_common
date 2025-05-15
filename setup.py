from setuptools import setup, find_packages

setup(
    name="ddomlab_eln_packages_common",
    version="0.1.0",
    package_dir={"":"src"},
    packages=find_packages(where="src"),
    author="Kyle Hollars",
    author_email="kmhollar@ncsu.edu",
    python_requires=">=3.11",
)
