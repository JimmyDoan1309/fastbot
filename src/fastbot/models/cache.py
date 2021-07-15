class NluCache:
    def __init__(self, text):
        self.processed_text = text
        self.tokenized_text = None
        self.dense_embedding_vector = None
        self.sparse_embedding_vector = None
        self.classifiers_output = {}
