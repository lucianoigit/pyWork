from setuptools import setup, find_packages

setup(
    name="pyWork",
    version="0.0.1",
    description="Un framework minimalista con Jinja2, Pydantic, y soporte para inyección de dependencias",
    author="Luciano Iriarte",
    author_email="lucianoiriartegit@gmail.com",
    packages=find_packages(include=['pywork', 'pywork.*']),  # Incluye pywork y sus submódulos
    include_package_data=True,  # Incluir archivos de datos como plantillas y archivos estáticos
    install_requires=[
        "starlette",
        "uvicorn",
        "jinja2",
        "pydantic",
        "aiofiles",  # Para servir archivos estáticos
    ],
    entry_points={
        'console_scripts': [
            'create-pywork=pywork.scripts:create_project',  # Comando para crear un proyecto nuevo
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
