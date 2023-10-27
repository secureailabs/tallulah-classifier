import asyncio
import os
import re

import dotenv
from numpy import rec
from pandas import DataFrame

from app.email_dao_mongo import EmailDaoMongo


async def main():
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    email_dao = EmailDaoMongo("mongodb://127.0.0.1:27017", "tallulah", "emails_temp")
    list_email_db = await email_dao.read_all()
    dict_source = {}
    for email in list_email_db:
        for annotation in email.annotations:
            if annotation.source not in dict_source:
                dict_source[annotation.source] = []

    print(dict_source)
    list_id = []
    list_date = []
    list_name = []
    list_email = []
    list_phone = []
    list_message = []
    for email in list_email_db:
        list_id.append(email.body["id"])
        list_date.append(email.received_time)
        list_name.append(list(email.from_address.values())[0])
        list_email.append(list(email.from_address.keys())[0])

        list_phone.append(email.body["phone"])
        list_message.append(email.body["content"])
        for source in dict_source:
            annotation = email.get_annotation(source)
            if annotation is not None:
                dict_source[source].append(annotation.label)
            else:
                dict_source[source].append(None)

    df = DataFrame()
    df["id"] = list_id
    df["date"] = list_date
    df["name"] = list_name
    df["email"] = list_email
    df["phone"] = list_phone
    df["message"] = list_message
    for source in dict_source:
        df[source] = dict_source[source]
    df.to_csv("test.csv", index=False)


if __name__ == "__main__":
    asyncio.run(main())
