import asyncio
from uuid import uuid4

from email_test import read_emails

from app.email_dao_mongo import EmailDaoMongo


async def main():
    email_dao = EmailDaoMongo("mongodb://127.0.0.1:27017", "tallulah", "emails_temp")

    await email_dao.delete_all()
    result = await email_dao.read_all()
    if 0 < len(result):
        raise Exception("Should be empty")
    list_email = read_emails(filter_no_body=False)
    for email in list_email:
        await email_dao.create(email)
    result = await email_dao.read_all()

    count_total = len(result)
    count_nonempty = 0
    count_nonemptylabeled = 0
    dict_label = {}
    for email in result:
        if 0 < len(email.body["content"].strip()):
            count_nonempty += 1
            if 0 < len(email.annotations):
                count_nonemptylabeled += 1
            if 1 < len(email.annotations):
                raise Exception("Should only have one annotation")
            if 0 < len(email.annotations):
                label = email.annotations[0].label
                if label not in dict_label:
                    dict_label[label] = 0
                dict_label[label] += 1

    print(f"Total emails: {count_total}")
    print(f"Non-empty emails: {count_nonempty}")
    print(f"Non-empty labeled emails: {count_nonemptylabeled}")
    for label in dict_label.keys():
        print(f"{label}: {dict_label[label]}")


if __name__ == "__main__":
    asyncio.run(main())
