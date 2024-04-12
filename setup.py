import pathlib
from distutils.core import setup

long_description = pathlib.Path("README.rst").read_text()

setup(
    name="constable",
    packages=["constable"],
    version="0.3.1",
    license="MIT",
    description="One decorator for lazy debugging. Inserts print statements directly into your AST.",
    long_description=long_description,
    long_description_content_type= 'text/x-rst',
    author="Saurabh Pujari",
    author_email="saurabhpuj99@gmail.com",
    url="https://github.com/saurabh0719/constable",
    keywords=[
        "debugger", 
        "decorator", 
        "tracker",
        "state tracker", 
        "variable state", 
        "timer", 
    ],
    project_urls={
        "Documentation": "https://github.com/saurabh0719/constable#README",
        "Source": "https://github.com/saurabh0719/constable",
    },
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)
