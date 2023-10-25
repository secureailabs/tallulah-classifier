import asyncio
from uuid import uuid4

from email_test import read_emails

from app.email_dao_mongo import EmailDaoMongo
from app.models.common import PyObjectId
from app.models.email import Annotation


async def main():
    email_dao = EmailDaoMongo("mongodb://127.0.0.1", "27017", "tallulah", "emails_temp")

    await email_dao.delete_all()
    result = await email_dao.read_all()
    print(len(result))
    list_email = read_emails()
    for email in list_email[0:10]:
        result = await email_dao.create(email)

    result = await email_dao.read_all()
    print(len(result))
    email_id = result[0].id
    result = await email_dao.read(email_id)
    print(len(result.annotations))
    await email_dao.add_annotation(email_id, Annotation(source="test", label="test", label_scores={"test": 0.5}))
    result = await email_dao.read(email_id)
    print(len(result.annotations))
    await email_dao.add_annotation(email_id, Annotation(source="test", label="test2", label_scores={"test": 0.5}))
    result = await email_dao.read(email_id)
    print(len(result.annotations))
    await email_dao.add_annotation(email_id, Annotation(source="test2", label="test", label_scores={"test": 0.5}))
    result = await email_dao.read(email_id)
    print(len(result.annotations))
    await email_dao.delete_all()


asyncio.run(main())
