from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="adimis_toolbox_core",
    version="0.0.2",
    description="Adimis Toolbox Core is a Django-based package designed for executing and scheduling graph based automated workflows while maintaining a knowledge base. This package includes several Django apps that can be easily integrated into your Django projects.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Aditya Mishra",
    author_email="aditya.mishra@adimis.in",
    url="https://github.com/adimis-ai/adimis_toolbox_core",
    packages=find_packages(include=["adimis_toolbox_core", "adimis_toolbox_core.*"]),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)
