from fastbot.nlu.component import BaseComponent
from fastbot.models import NluData, Message


class SampleCounter(BaseComponent):
    """
    A simple component that demonstrate how to use custom component with interpreter
    All it does is count how many samples in the dataset during the training/testing phase and 
    do nothting during the process Message phase.

    For more information, please check BaseComponent for all the functions you can override
    """
    def train(data: NluData):
        print(f'Total of {len(data.all_samples)} samples in training dataset')

    def process(message: Message):
        pass
