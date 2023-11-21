import asyncio
import os
from typing import Dict, List
from uuid import uuid4

import dotenv
import pandas
from pydantic import StrictStr

# Importing custom modules
from app.email_dao_mongo import EmailDaoMongo
from app.models.common import PyObjectId
from app.models.email import Annotation, Email_Base


def read_emails_for_file(name_file: str, filter_no_body=True) -> List[Email_Base]:
    """
    _summary_: Read the emails from the csv file.

    """
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    # Get the path to the raw dataset directory from environment variables
    path_dir_data = os.environ.get("PATH_DIR_DATASET_RAW")
    if path_dir_data is None:
        raise ValueError("Please set PATH_DIR_DATASET_RAW")

    # Construct the full path to the specified CSV file
    path_file_data = os.path.join(path_dir_data, "tbbca", name_file)

    # Read the CSV file into a pandas DataFrame
    data_frame_data = pandas.read_csv(
        path_file_data, header=0, keep_default_na=False, dtype={"ID": str, "Tags": str, "Phone": str, "Message": str}
    )

    list_email = []
    for index, row in data_frame_data.iterrows():
        # Extract relevant data from the row
        subject: StrictStr = ""
        body: Dict = {}
        body["content"] = row["Message"]
        body["phone"] = row["Phone"]
        body["status"] = row["Status"]
        body["id"] = row["Id"]

        from_address: Dict = {row["Email"]: row["Name"]}
        if row["Date"].strip() == "Date":
            continue
        if len(row["Date"].strip()) == 0:
            continue
        if filter_no_body:
            if len(body["content"].strip()) == 0:
                continue

        received_time: str = row["Date"]  # datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S")
        mailbox_id: str = str(uuid4())
        annotations = []
        label = row["Tags"].strip()

        # Correct some typos in the labels
        if label == "in a trial":
            label = "In a trial"

        if label == "Recent recurrence":
            label = "Recent Reccurance"

        # Map "Recent Reccurance" to "Newly Diagnosed"
        if label == "Recent Reccurance":
            label = "Newly Diagnosed"
            print("Recent Reccurance -> Newly Diagnosed")

        if 0 < len(label):
            # If there is a label, add it to the annotations
            annotations.append(
                Annotation(
                    source="csv",
                    label=label,
                    label_scores={label: 1.0},
                )
            )

        dict_data = {
            "subject": subject,
            "body": body,
            "from_address": from_address,
            "received_time": received_time,
            "mailbox_id": mailbox_id,
            "annotations": annotations,
            "user_id": mailbox_id,
            "outlook_id": mailbox_id,
        }

        # Create an Email_Base instance using Pydantic
        email = Email_Base(**dict_data)
        list_email.append(email)

    return list_email


def read_emails(filter_no_body=True) -> List[Email_Base]:
    # Read emails from two different files and merge them
    list_email = read_emails_for_file("20231023_wwt_tags.csv", filter_no_body)
    list_email_add = read_emails_for_file("20231031_wwt_tags.csv", True)
    dict_email = {}

    # Create a dictionary for quick lookup based on email body ID
    for email in list_email_add:
        if 0 < len(email.annotations):
            dict_email[email.body["id"]] = email

    # Move over the additional annotations to the main list
    for email in list_email:
        if email.body["id"] in dict_email:
            if len(email.annotations) == 0:
                email.annotations = dict_email[email.body["id"]].annotations

    return list_email


async def main():
    # Initialize an instance of EmailDaoMongo for MongoDB connection
    email_dao = EmailDaoMongo("mongodb://127.0.0.1:27017", "tallulah", "emails_temp")

    # Delete all existing emails in the database
    await email_dao.delete_all()
    result = await email_dao.read_all()
    if 0 < len(result):
        raise Exception("Should be empty")

    # Read emails from CSV files
    list_email = read_emails(filter_no_body=False)

    # Create emails in the database
    for email in list_email:
        await email_dao.create(email)

    # Read all emails from the database
    result = await email_dao.read_all()

    count_total = len(result)
    count_nonempty = 0
    count_nonemptylabeled = 0
    dict_label = {}

    # Analyze the emails in the database
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
    # Run the asynchronous main function using asyncio
    asyncio.run(main())
