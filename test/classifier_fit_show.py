import asyncio
import os

import dotenv
from sklearn.metrics import classification_report, confusion_matrix

from app.email_classifier_tfid import EmailClassifierTfid
from app.email_dao_mongo import EmailDaoMongo
from app.utils.secrets import get_secret


async def main():
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    email_dao = EmailDaoMongo("mongodb://127.0.0.1", "27017", "tallulah", "emails_temp")
    list_email = await email_dao.read_all()

    path_file_model = get_secret("path_file_model")
    dict_score_multiplier = {
        "General Breasties": 0.9,
        "General Info": 0.5,
        "In a trial": 1.0,
        "Interested in a trial": 1.0,
        "Newly Diagnosed": 1.0,
        "Partners": 1.5,
        "Recent Reccurance": 1.0,
    }

    classfier = EmailClassifierTfid(40)
    classfier.fit(list_email, "csv", dict_score_multiplier)
    classfier.save(path_file_model)

    list_label_true = []
    list_label_pred = []
    for email in list_email:
        if 0 < len(email.body["content"].strip()):
            annotation_true = email.get_annotation("csv")
            if annotation_true is not None:
                annotation_pred = classfier.predict_email_tags(email)[0]
                await email_dao.add_annotation(email.id, annotation_pred)
                list_label_true.append(annotation_true.label)
                list_label_pred.append(annotation_pred.label)

    list_label = classfier.model.list_label
    matrix = confusion_matrix(list_label_true, list_label_pred, labels=list_label)
    print(matrix)
    for index, label in enumerate(list_label):
        for index2, label2 in enumerate(list_label):
            if matrix[index][index2] > 0:
                if label != label2:
                    print(f"{label} -> {label2}: {matrix[index][index2]}")
    print(classification_report(list_label_true, list_label_pred, labels=list_label, zero_division=0))


if __name__ == "__main__":
    asyncio.run(main())
