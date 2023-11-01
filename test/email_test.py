import os
from datetime import datetime
from typing import Dict, List
from uuid import uuid4

import dotenv
import pandas
from pydantic import StrictStr

from app.models.common import PyObjectId
from app.models.email import Annotation, Email_Base


def read_emails_for_file(name_file: str, filter_no_body=True) -> List[Email_Base]:
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    path_dir_data = os.environ.get("PATH_DIR_DATASET_RAW")
    if path_dir_data is None:
        raise ValueError("Please set PATH_DIR_DATASET_RAW")

    path_file_data = os.path.join(path_dir_data, "tbbca", name_file)

    data_frame_data = pandas.read_csv(
        path_file_data, header=0, keep_default_na=False, dtype={"ID": str, "Tags": str, "Phone": str, "Message": str}
    )

    list_email = []
    dict_label = {}
    for index, row in data_frame_data.iterrows():
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
        # correct some typos
        if label == "in a trial":
            label = "In a trial"

        if label == "Recent recurrence":
            label = "Recent Reccurance"
        # map recent recurrence  to newly diagnosed
        if label == "Recent Reccurance":
            label = "Newly Diagnosed"
            print("Recent Reccurance -> Newly Diagnosed")
        if 0 < len(label):
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
        }
        email = Email_Base(**dict_data)
        list_email.append(email)

    return list_email


def read_emails(filter_no_body=True) -> List[Email_Base]:
    list_email = read_emails_for_file("20231023_wwt_tags.csv", filter_no_body)
    list_email_add = read_emails_for_file("20231031_wwt_tags.csv", True)
    dict_email = {}
    for email in list_email_add:
        if 0 < len(email.annotations):
            dict_email[email.body["id"]] = email
    # move over the addtional annotations
    for email in list_email:
        if email.body["id"] in dict_email:
            if len(email.annotations) == 0:
                email.annotations = dict_email[email.body["id"]].annotations
            # print(dict_email[email.body["id"]].annotations)

    return list_email
