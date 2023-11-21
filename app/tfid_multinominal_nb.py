from typing import Dict, List, Optional

from numpy import multiply
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


class TfidMultinominalNb:
    def __init__(self, max_features: int = 1000):
        self.encoder = TfidfVectorizer(max_features=max_features)  # You can adjust the number of features
        self.classifier = MultinomialNB()
        self.list_label: List[str] = []
        self.dict_label: Dict[str, int] = {}
        self.dict_score_multiplier: Dict[str, float] = {}

    def fit(
        self, list_text: List[str], list_text_label: List[str], dict_score_multiplier: Optional[Dict[str, float]] = {}
    ):
        X_transformed = self.encoder.fit_transform(list_text)
        self.classifier.fit(X_transformed, list_text_label)
        self.list_label = self.classifier.classes_  # type: ignore
        self.dict_label = {}
        for i, label in enumerate(self.list_label):
            self.dict_label[label] = i
        if dict_score_multiplier is None:
            self.dict_score_multiplier = {}
        else:
            self.dict_score_multiplier = dict_score_multiplier.copy()
        for label in self.list_label:
            if label not in self.dict_score_multiplier:
                self.dict_score_multiplier[label] = 1.0

    def predict(self, text: str) -> Dict[str, float]:
        encoding = self.encoder.transform([text])
        y_pred = self.classifier.predict_proba(encoding)
        dict_result = {}
        for i, label in enumerate(self.classifier.classes_):
            multiplier = self.dict_score_multiplier[label]
            dict_result[label] = y_pred[0][i] * multiplier
        return dict_result
