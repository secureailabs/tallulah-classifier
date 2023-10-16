import cloudpickle as cpkl

from app.models.email import Email_Base


class EmailClassifier:
    """The email classifier"""

    def __init__(self):
        pass

    def load(self, model_path: str):
        with open(model_path, "rb") as f:
            self.model = cpkl.load(f)

    def save(self, model_path: str):
        with open(model_path, "wb") as f:
            cpkl.dump(self.model, f)

    def predict_email_tags(self, email: Email_Base) -> str:
        """Predict the tags of an email"""
        # combine the subject and body of each email together and pass it in as text input; You can pass an array of emails

        content = email.body["content"]
        result = self.model.predict(content)
        print(result[0])
        return result[0]
