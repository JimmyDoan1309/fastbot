from . import generate_nlu_data
from . import create
import fire


def main():
    fire.Fire({
        'generate_nlu_data': generate_nlu_data.run,
        'create': create.run,
    })
