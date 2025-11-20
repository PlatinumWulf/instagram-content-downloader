#!/usr/bin/env python3
"""
Setup script dla Instagram Content Downloader
Instalacja: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Przeczytaj README dla long_description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Przeczytaj requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="instagram-content-downloader",
    version="3.0.0",
    description="Zaawansowane narzędzie do pobierania zawartości z profili Instagram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/instagram-content-downloader",
    license="MIT",

    # Pakiety
    packages=find_packages(exclude=['tests', 'tests.*']),

    # Wymagane biblioteki
    install_requires=requirements,

    # Python version
    python_requires=">=3.8",

    # Entry points - skrypty CLI
    entry_points={
        'console_scripts': [
            'ig-downloader=main:main',
            'instagram-downloader=main:main',
        ],
    },

    # Klasyfikatory
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Utilities",
    ],

    # Słowa kluczowe
    keywords="instagram downloader scraper social-media photos videos",

    # Pliki danych do uwzględnienia
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.md', '*.example', '.env.example'],
    },

    # Extras dla development
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
        'browser': [
            'selenium>=4.0.0',
        ],
    },
)
