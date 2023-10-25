import asyncio
from typing import Dict, List
from uuid import uuid4

from app.email_dao_mongo import EmailDaoMongo
from app.models.email import Annotation


async def main():
    email_dao = EmailDaoMongo("mongodb://127.0.0.1", "27017", "tallulah", "emails_temp")
    list_email = await email_dao.read_all()
    dict_annotation: Dict[str, List[Annotation]] = {}
    for email in list_email:
        annotation = email.get_annotation("csv")

        if annotation is not None:
            if annotation.label == "Partners":
                print("from_address")
                print(email.from_address)
                print("body")
                print(email.body["content"])


if __name__ == "__main__":
    asyncio.run(main())
