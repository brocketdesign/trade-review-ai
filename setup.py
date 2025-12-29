"""Setup script for Trade Review AI package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme = Path(__file__).parent / "README.md"
long_description = readme.read_text() if readme.exists() else ""

setup(
    name="trade-review-ai",
    version="0.1.0",
    description="Educational trade analysis system connecting market data with AI-powered insights",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Brocket Design",
    url="https://github.com/brocketdesign/trade-review-ai",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Education",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="trading analysis ai openai tradingview education",
    project_urls={
        "Bug Reports": "https://github.com/brocketdesign/trade-review-ai/issues",
        "Source": "https://github.com/brocketdesign/trade-review-ai",
    },
)
