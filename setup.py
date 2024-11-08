from setuptools import setup, find_packages

# Load dependencies from requirements.txt
with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

setup(
    name="pyWork",
    version="0.0.1",  # Increment version to reflect changes
    description="This framework is designed to simplify the development of web applications by providing an easy-to-use interface for rendering templates with Jinja2, validating data with Pydantic, and managing dependencies through a robust container system. It allows developers to focus on building features while ensuring clean, maintainable, and testable code",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Luciano Iriarte",
    author_email="lucianoiriartegit@gmail.com",
    url="https://github.com/lucianoigit/pywork",  # Your GitHub repository URL
    packages=find_packages(include=['pywork', 'pywork.*']),  # Includes pywork and its submodules
    include_package_data=True,  # Include data files like templates and static files
    install_requires=requirements,  # Use dependencies loaded from requirements.txt
    entry_points={
        'console_scripts': [
            'pywork=pywork.scripts:manage_project',  # Command for creating or cleaning projects
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
