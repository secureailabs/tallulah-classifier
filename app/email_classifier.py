from typing import List
from uuid import uuid4

import cloudpickle as cpkl

from app.models.email import Annotation, Email_Base
from app.tfid_multinominal_nb import TfidMultinominalNb


class EmailClassifier:
    """The email classifier"""

    def __init__(self):
        self.is_loaded = False
        pass

    def load(self, model_path: str):
        with open(model_path, "rb") as f:
            self.model = cpkl.load(f)
        self.is_loaded = True

    def save(self, model_path: str):
        with open(model_path, "wb") as f:
            cpkl.dump(self.model, f)

    def fit(self, list_email: List[Email_Base]):
        self.model = TfidMultinominalNb()
        list_text = []
        list_text_label = []
        for email in list_email:
            if 0 < len(email.annotations):
                text = email.body["content"]
                label = list(email.annotations[0].values.keys())[0]
                list_text.append(text)
                list_text_label.append(label)

        self.model.fit(list_text, list_text_label)
        self.is_loaded = True

    def predict_email_tags(self, email: Email_Base) -> List[Annotation]:
        """Predict the tags of an email"""
        if not self.is_loaded:
            raise ValueError("Please load the model first")
        # combine the subject and body of each email together and pass it in as text input; You can pass an array of emails

        content = email.body["content"]
        dict_result = self.model.predict(content)
        tag_predicted = max(dict_result, key=dict_result.get)
        annotation = Annotation(
            annotation_id=str(uuid4()),
            source="TfidMultinominalNb",
            values={tag_predicted: 1.0},
        )
        return [annotation]
