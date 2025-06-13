"""
Setup configuration for auto_codex package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Define requirements directly (since we're creating the structure)
requirements = [
    'pydantic>=2.0.0',
    'jinja2>=3.0.0',
    'pyyaml>=6.0.0',
    'colorama>=0.4.6',
]

setup(
    name='auto_codex',
    version='0.1.0',
    description='Advanced automation framework for Codex AI with comprehensive health monitoring, multi-provider support, and powerful log parsing capabilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Joseph Schlesinger/auto_codex',
    author='Joseph Schlesinger',
    author_email='joe@schlesinger.io',
    license='MIT',
    
    # Classifiers help users find your project by categorizing it
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    
    keywords='ai codex automation health-monitoring multi-provider log-parsing',
    
    # Package configuration
    packages=find_packages(exclude=['tests*', 'examples*', 'docs*']),
    python_requires='>=3.8',
    install_requires=requirements,
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    
    # Include package data
    include_package_data=True,
    package_data={
        'auto_codex': ['py.typed'],
    },
    
    # Entry points for command-line interface
    entry_points={
        'console_scripts': [
            'auto-codex=auto_codex.core:main',
        ],
    },
    
    # Project URLs
    project_urls={
        'Bug Reports': 'https://github.com/Joseph Schlesinger/auto_codex/issues',
        'Source': 'https://github.com/Joseph Schlesinger/auto_codex',
        'Documentation': 'https://auto-codex.readthedocs.io/',
    },
) 