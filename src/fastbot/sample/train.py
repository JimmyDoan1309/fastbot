from fastbot.nlu.interpreter_builder import InterpreterBuilder
from fastbot.nlu.utils import load_nlu_data


def train_nlu():
    interpreter = InterpreterBuilder.load('./interpreter.yaml', verbose=1)
    data = load_nlu_data('./nlu_data.yaml')
    interpreter.train(data)
    interpreter.save('./model/nlu')
    print('Interpreter finished training and saved at ./model/nlu')


if __name__ == '__main__':
    train_nlu()
