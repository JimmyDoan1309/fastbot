class NluCache:
    def __init__(self, text):
        self.processed_text = text
        self.tokenized_text = []
        self.pos_tag = {}
        self.classifiers_output = {}
        self.dense_embedding_vector = None
        self.sparse_embedding_vector = None

    def to_json(self):
        return {
            "processed_text": self.processed_text,
            "tokenzied_text": self.tokenized_text,
            "pos_tag": self.pos_tag,
            "classifiers_output": self.classifiers_output,
        }

    @classmethod
    def from_json(cls, json: dict):
        cache = cls(json['processed_text'])
        cache.tokenized_text = json['tokenzied_text']
        cache.pos_tag = json['pos_tag']
        cache.classifiers_output = json['classifiers_output']
