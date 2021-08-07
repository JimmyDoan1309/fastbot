import os
import shutil
import fastbot


def run(path: str = './', bare: bool = False):
    path = os.path.abspath(path)
    root = os.path.dirname(fastbot.__file__)
    if not bare:
        shutil.copytree(f'{root}/sample/simple', path, dirs_exist_ok=True)
    if bare:
        shutil.copytree(f'{root}/sample/bare', path, dirs_exist_ok=True)
