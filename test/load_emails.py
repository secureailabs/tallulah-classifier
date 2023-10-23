import asyncio
from uuid import uuid4

from email_test import read_emails

from app.email_dao_mongo import EmailDaoMongo


async def main():
    email_dao = EmailDaoMongo("mongodb://127.0.0.1", "27017", "tallulah", "emails_temp")

    await email_dao.delete_all()
    result = await email_dao.read_all()
    if 0 < len(result):
        raise Exception("Should be empty")
    list_email = read_emails(filter_no_body=False)
    for email in list_email:
        await email_dao.create(email)
    result = await email_dao.read_all()
    print(len(result))


if __name__ == "__main__":
    asyncio.run(main())
