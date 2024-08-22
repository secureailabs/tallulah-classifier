import asyncio
import os

import dotenv

from app.email_classifier_tfid import EmailClassifierTfid
from app.email_dao_mongo import EmailDaoMongo


async def main():
    """Test the email classifier"""
    email_dao = EmailDaoMongo("emails_temp")

    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    path_dir_model_cache = os.environ.get("PATH_DIR_MODEL_CACHE")
    if path_dir_model_cache is None:
        raise ValueError("Please set PATH_DIR_MODEL_CACHE")

    path_file_model = os.path.join(path_dir_model_cache, "email_model.pkl")
    list_email = await email_dao.read_all()

    classfier = EmailClassifierTfid()
    if os.path.isfile(path_file_model):
        classfier.load(path_file_model)
    else:
        classfier.fit(list_email, "model_test")
        classfier.save(path_file_model)
    # count correct
    count = 0
    count_total = 0
    for email in list_email:
        # print(tag)
        if len(email.annotations) == 0:
            continue
        else:
            count_total += 1

        label_pred = classfier.predict_email_tags(email)[0].label
        label_true = email.annotations[0].label
        if label_pred == label_true:
            count += 1

    print(f"accuracy: {count/count_total}")


if __name__ == "__main__":
    asyncio.run(main())
