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
