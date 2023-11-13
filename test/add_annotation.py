import asyncio
import random
import sys
from typing import List

from app.email_dao_mongo import EmailDaoMongo
from app.models.email import Annotation, Email_Db


def print_email(email: Email_Db):
    print(f"\n\n\nfrom_address: \n{list(email.from_address.keys())[0]}")
    if not email.body:
        print(f"body: \nNo body")
        return
    content = email.body["content"]
    if 0 < len(content):
        print(f"body: \n{content}")
    else:
        print(f"body: \nNo body")


def print_option(list_label: List[str]):
    list_option = []
    list_option.append("q")
    list_option.append("s")
    for index, option in enumerate(list_label):
        print(f"({index + 1}): {option}")
        list_option.append(str(index + 1))
    print(f"(q): quit")
    print(f"(s): skip")
    while True:
        option = input("Please choose an option: ")
        if option in list_option:
            break
        else:
            print("Invalid option")
    if option == "q":
        exit(0)
    if option == "s":
        return None
    else:
        return list_label[int(option) - 1]


async def main():
    if len(sys.argv) < 2:
        print("Please provide a annotation_source to add annotations to")
        exit(1)
    annotation_source = sys.argv[1]
    email_dao = EmailDaoMongo("mongodb://127.0.0.1:27017", "tallulah", "emails_temp")
    list_result = await email_dao.read_all()
    list_label = [
        "General Breasties",
        "General Info",
        "In a trial",
        "Partners",
        "Interested in a trial",
        "Newly Diagnosed",
        "Recent Reccurance",
    ]
    random_indexes = list(range(len(list_result)))
    random.shuffle(random_indexes)
    for index in random_indexes:
        email = list_result[index]
        print_email(email)
        label = print_option(list_label)
        if label is None:
            continue
        else:
            await email_dao.add_annotation(
                email.id, Annotation(source=annotation_source, label=label, label_scores={label: 1.0})
            )

    #


if __name__ == "__main__":
    asyncio.run(main())
