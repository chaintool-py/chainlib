from setuptools import setup
import configparser
import os


requirements = []
f = open('requirements.txt', 'r')
while True:
    l = f.readline()
    if l == '':
        break
    requirements.append(l.rstrip())
f.close()

setup(
        install_requires=requirements,
        extras_require={
             'xdg': "pyxdg~=0.27",
             },
        license_files= ('LICENSE',),
        python_requires = '>=3.7',
        include_package_data = True,
        packages = [
            'chainlib',
            'chainlib.cli',
            'chainlib.runnable',
            ],
        scripts = [
            'scripts/chainlib-man.py',
            ],
    )
