#!/usr/bin/env python3
"""
Setup Script - سكريبت التثبيت
ملف إعداد المشروع كحزمة Python
"""

from setuptools import setup, find_packages
import os

# قراءة ملف README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# قراءة ملف requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bot-factory-maker",
    version="2.0.0",
    author="Bot Factory Team",
    author_email="contact@botfactory.com",
    description="مصنع البوتات - نظام متكامل لإنشاء وإدارة البوتات",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/bot-factory-maker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "bot-factory=main:main",
            "bfm=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="telegram bot factory maker pyrogram",
    project_urls={
        "Bug Reports": "https://github.com/username/bot-factory-maker/issues",
        "Source": "https://github.com/username/bot-factory-maker",
        "Documentation": "https://github.com/username/bot-factory-maker/blob/main/README.md",
    },
)