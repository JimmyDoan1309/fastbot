import argparse
import os

COMMANDS = ['init', 'train']


parser = argparse.ArgumentParser()

parser.add_argument('command', choices=COMMANDS)


def main():
    args = parser.parse_args()
    command = args.command
    if command == 'init':
        project = input("Project name: ")
        os.makedirs(f'./{project}/nodes/', exist_ok=True)
        os.makedirs(f'./{project}/validators/', exist_ok=True)
        os.makedirs(f'./{project}/entity_extractors/', exist_ok=True)
        with open(f'./{project}/main.py', 'w'):
            pass
