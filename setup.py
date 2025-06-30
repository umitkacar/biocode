from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core requirements
CORE_REQUIREMENTS = [
    "pyjwt>=2.8.0",
]

# Optional requirements for different features
EXTRAS_REQUIRE = {
    "metrics": [
        "prometheus-client>=0.19.0",
        "psutil>=5.9.6",
    ],
    "dashboard": [
        "aiohttp>=3.9.1",
        "matplotlib>=3.8.2",
        "pandas>=2.1.4",
    ],
    "distributed": [
        "redis>=5.0.1",
        "aiocache>=0.12.2",
    ],
    "dev": [
        "pytest>=7.4.3",
        "pytest-asyncio>=0.23.2",
        "black>=23.12.1",
        "mypy>=1.8.0",
        "ruff>=0.1.9",
        "coverage>=7.3.4",
    ],
    "all": [
        "prometheus-client>=0.19.0",
        "aiohttp>=3.9.1",
        "psutil>=5.9.6",
        "matplotlib>=3.8.2",
        "pandas>=2.1.4",
        "redis>=5.0.1",
        "aiocache>=0.12.2",
    ],
}

setup(
    name="biocode",
    version="0.2.0",
    author="Umit Kacar, PhD",
    author_email="[Contact information to be provided]",
    description="BioCode - Autonomous Problem-Solving Framework with biological architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/umitkacar/BioCode",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=CORE_REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    license="Proprietary - All Rights Reserved by Umit Kacar, PhD",
)