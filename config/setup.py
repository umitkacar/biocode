from setuptools import setup, find_packages
import os

# Read README for long description
readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
with open(readme_path, "r", encoding="utf-8") as fh:
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
    version="0.1.0",
    author="BioCode Team",
    author_email="team@biocode.dev",
    description="Living Code Architecture - A biological approach to software organization with self-healing capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/umityigitbsrn/biocode",
    packages=find_packages(where="../"),
    package_dir={"": "../"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=CORE_REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
)