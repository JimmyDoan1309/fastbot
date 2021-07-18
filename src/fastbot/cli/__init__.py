from fastbot.cli import generate_nlu_data
import fire

def main():
    fire.Fire({
        'generate_nlu_data': generate_nlu_data.run
    })