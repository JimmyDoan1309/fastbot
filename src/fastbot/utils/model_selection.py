from fastbot.schema.nlu_data import NluData
import numpy as np


def train_test_split(data: NluData, split_ratio: float = 0.2, shuffle=True, seed=None):
    np.random.seed(seed)

    train_data = {}
    test_data = {}

    for intent, samples in data.intents.items():
        if shuffle:
            np.random.shuffle(samples)

        samples_size = len(samples)
        test_size = int(np.floor(samples_size*split_ratio))
        train_size = samples_size - test_size
        train_data[intent] = samples[:train_size]

        if test_size != 0:
            test_data[intent] = samples[train_size:train_size+test_size]

    np.random.seed(None)
    return NluData(train_data), NluData(test_data)
