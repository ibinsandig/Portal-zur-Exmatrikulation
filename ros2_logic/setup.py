from setuptools import setup, find_packages

setup(
    name='ros2_logic',
    version='0.1.0',
    packages=find_packages(),      # findet automatisch alles im Ordner
    install_requires=[
        # hier deine Python-Abhängigkeiten eintragen, z.B. numpy, requests
    ],
    author='Chaos Dev Team',
    description='Chaos Logic Python Package',
    python_requires='>=3.10',
)
