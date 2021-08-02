import os
import shutil
import fastbot


def run(path: str = './'):
    path = os.path.abspath(path)
    root = os.path.dirname(fastbot.__file__)
    shutil.copytree(f'{root}/sample', path, dirs_exist_ok=True)
