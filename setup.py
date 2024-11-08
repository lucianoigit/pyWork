from setuptools import setup, find_packages

# Cargar dependencias de requirements.txt
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = fh.read().splitlines()
except Exception as e:
    print("Error loading requirements.txt:", e)
    requirements = []

# Cargar descripción desde README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except Exception as e:
    print("Error loading README.md:", e)
    long_description = ""

setup(
    name="pywork-framework",
    version="0.0.1",
    description="This framework is designed to simplify the development of web applications by providing an easy-to-use interface for rendering templates with Jinja2, validating data with Pydantic, and managing dependencies through a robust container system.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Luciano Iriarte",
    author_email="lucianoiriartegit@gmail.com",
    url="https://github.com/lucianoigit/pywork",
    packages=find_packages(include=['pywork', 'pywork.*']),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pywork=pywork.scripts:manage_project',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
