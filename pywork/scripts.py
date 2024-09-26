import os
import sys
import shutil

def create_project():
    if len(sys.argv) < 2:
        print("Por favor, especifica el nombre del proyecto.")
        sys.exit(1)

    project_name = sys.argv[1]
    project_path = os.path.join(os.getcwd(), project_name)

    try:
        # Crear la estructura de carpetas
        os.makedirs(os.path.join(project_path, 'templates'))
        os.makedirs(os.path.join(project_path, 'static'))
        os.makedirs(os.path.join(project_path, 'routes'))
        os.makedirs(os.path.join(project_path, 'services'))
        os.makedirs(os.path.join(project_path, 'models'))

        # Crear archivos iniciales
        with open(os.path.join(project_path, 'main.py'), 'w') as f:
            f.write(
                '''from pywork import Framework

app = Framework()

if __name__ == "__main__":
    app.run()
'''
            )

        with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
            f.write(
                '''starlette
uvicorn
jinja2
pydantic
aiofiles
'''
            )

        print(f"Proyecto {project_name} creado exitosamente.")

    except Exception as e:
        print(f"Error al crear el proyecto: {e}")
