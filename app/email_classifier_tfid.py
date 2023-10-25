from typing import Dict, List, Optional
from uuid import uuid4

import cloudpickle as cpkl

from app.models.email import Annotation, Email_Base
from app.tfid_multinominal_nb import TfidMultinominalNb


class EmailClassifierTfid:
    """The email classifier"""

    def __init__(self, max_features: int = 1000):
        self.is_loaded = False
        self.model_type = "TfidMultinominalNb"
        self.max_features = max_features

    def load(self, model_path: str):
        with open(model_path, "rb") as f:
            self.model = cpkl.load(f)
        self.is_loaded = True

    def save(self, model_path: str):
        with open(model_path, "wb") as f:
            cpkl.dump(self.model, f)

    def fit(
        self,
        list_email: List[Email_Base],
        annotation_source: str,
        dict_score_multiplier: Optional[Dict[str, float]] = None,
    ):
        self.model = TfidMultinominalNb(self.max_features)
        list_text = []
        list_text_label = []
        for email in list_email:
            annotation_selected = email.get_annotation(annotation_source)
            if annotation_selected is not None:
                text = email.body["content"]
                label = annotation_selected.label
                if 0 < len(text.strip()):
                    list_text.append(text)
                    list_text_label.append(label)

        self.model.fit(list_text, list_text_label, dict_score_multiplier)
        self.is_loaded = True

    def predict_email_tags(
        self,
        email: Email_Base,
    ) -> List[Annotation]:
        """Predict the tags of an email"""
        if not self.is_loaded:
            raise ValueError("Please load the model first")
        # combine the subject and body of each email together and pass it in as text input; You can pass an array of emails

        content = email.body["content"]

        dict_result = self.model.predict(content)
        if 0 == len(content.strip()):  # empty messages are always general info
            for key in dict_result.keys():
                dict_result[key] = 0.0
            dict_result["General Info"] = 1.0

        tag_predicted = max(dict_result, key=dict_result.get)
        annotation = Annotation(
            source=self.model_type,
            label=tag_predicted,
            label_scores=dict_result,
        )

        return [annotation]
