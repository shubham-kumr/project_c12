"""
Setup script for Project-C12 Carbon-Aware Model Router.
"""

from setuptools import setup, find_packages

# Read requirements from requirements-dashboard.txt
with open("requirements-dashboard.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="project-c12",
    version="0.1.0",
    description="A carbon-aware model router for selecting the most efficient AI models",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "project-c12-dashboard=src.dashboard.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 