#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sqlassistant",
    version="0.1.0",
    author="SQL助手团队",
    author_email="example@example.com",
    description="SQL助手 - 功能强大的SQL命令行工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/sqlassistant",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "typer>=0.7.0",
        "rich>=12.0.0",
        "SQLAlchemy>=2.0.0",
        "pandas>=1.5.0",
        "matplotlib>=3.5.0",
        "plotly>=5.5.0",
        "sqlparse>=0.4.3",
        "sqlglot>=10.4.0",
        "pyyaml>=6.0",
        "psycopg2-binary>=2.9.5",
        "torch>=2.0.1",
        "transformers>=4.28.0",
        "dashscope>=1.12.0",  # 阿里云Qwen API
        "deepseek>=0.1.0",    # DeepSeek API
    ],
    entry_points={
        "console_scripts": [
            "sqlassistant=sqlassistant.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: SQL",
        "Topic :: Database",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
) 