from fastbot.nlu.component import BaseComponent
from fastbot.models import NluData, Message


class SampleCounter(BaseComponent):
    """
    Sample Component to demonstrate how to use custom component
    with Fastbot's Interpreter

    This component will print out how many sample in the dataset
    in the traning step while do nothing at the process message step.
    """

    def get_metadata(self):
        """
        `type` must be the same as interpreter config file (path to import)
        Otherwise Fastbot will not know where to import the class when load.

        `name` can be anything. However if you have more than one component with
        the same type, their name must be different.
        """
        return {
            'name': 'my_sample_counter',
            'type': 'components.SampleCounter'
        }

    def train(self, data: NluData):
        print('Total samples: ', len(data.all_samples))
        return

    def process(self, message):
        pass
