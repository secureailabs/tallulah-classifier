from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


class TfidMultinominalNb:
    def __init__(self):
        self.encoder = TfidfVectorizer(max_features=1000)  # You can adjust the number of features
        self.classifier = MultinomialNB()
        self.list_label = None
        self.dict_label: Dict[str, int] = {}

    # def fit(self, list_label: List[str], list_text: List[str], list_text_label: List[str]):
    def fit(self, list_text: List[str], list_text_label: List[str]):
        # self.list_label = list_label
        # self.dict_label = {}
        # for i, label in enumerate(list_label):
        #    self.dict_label[label] = i
        X_transformed = self.encoder.fit_transform(list_text)
        self.classifier.fit(X_transformed, list_text_label)

    def predict(self, text: str) -> Dict[str, float]:
        encoding = self.encoder.transform([text])
        y_pred = self.classifier.predict_proba(encoding)
        dict_result = {}
        for i, label in enumerate(self.classifier.classes_):
            dict_result[label] = y_pred[0][i]
        return dict_result
