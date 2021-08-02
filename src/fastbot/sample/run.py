from fastbot import Agent
import os


def main():
    if not os.path.exists('./model/nlu'):
        raise Exception("Please train the intepreter first by running `python train.py`")
    agent = Agent('./model/nlu', './flow.yaml')
    agent.local_test()


if __name__ == '__main__':
    main()
