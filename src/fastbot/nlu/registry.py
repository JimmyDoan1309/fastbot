from .classifiers.sklearn_models import ForestClassifier, NeuralNetClassifier, KnnClassifier
from .classifiers.keras_models import ConvolutionClassifier
from .classifiers.ensemble import EnsembleClassifier
from .tokenizers.word_tokenizer import WordTokenizer
from .tokenizers.vietnamese_tokenizer import VietnameseTokenizer
from .vectorizers.fasttext import FasttextVectorizer
from .vectorizers.count_vector import CountVectorizer
from .vectorizers.tfidf_vector import TfidfVectorizer
from .preprocessors.casing import CasingProcessor
from .preprocessors.punc_remover import PunctuationRemover
from fastbot.utils.common import import_from_path
from typing import Text, Dict, Any


registered_component = [
    # Processors
    CasingProcessor,
    PunctuationRemover,
    # Classifiers
    ForestClassifier,
    NeuralNetClassifier,
    KnnClassifier,
    ConvolutionClassifier,
    EnsembleClassifier,
    # Tokenizers
    WordTokenizer,
    VietnameseTokenizer,
    # Vectorizers
    FasttextVectorizer,
    TfidfVectorizer,
    CountVectorizer
]

component_mapping = {component.__name__: component for component in registered_component}


def load_component(component_type: Text, path: Text, metadata: Dict[Text, Any], **kwargs):
    if component_mapping.get(component_type):
        component = component_mapping[component_type].load(path, metadata, **kwargs)
    else:
        component_class = import_from_path(component_type)
        component = component_class.load(path, metadata, **kwargs)
    return component


def get_component(component_type: Text):
    if component_mapping.get(component_type):
        return component_mapping[component_type]
    else:
        return import_from_path(component_type)
