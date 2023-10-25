import asyncio
import os

import dotenv

from app.email_classifier_tfid import EmailClassifierTfid
from app.email_dao_mongo import EmailDaoMongo
from app.utils.secrets import get_secret


async def main():
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    email_dao = EmailDaoMongo("mongodb://127.0.0.1", "27017", "tallulah", "emails_temp")
    list_email = await email_dao.read_all()
    path_file_model = get_secret("path_file_model")
    classfier = EmailClassifierTfid()
    if os.path.isfile(path_file_model):
        classfier.load(path_file_model)

    for email in list_email:
        if email.get_annotation("csv") is not None:
            list_annotation = classfier.predict_email_tags(email)
            for annotation in list_annotation:
                await email_dao.add_annotation(email.id, annotation)


if __name__ == "__main__":
    asyncio.run(main())
