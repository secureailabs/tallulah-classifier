import os
from datetime import datetime
from typing import Dict
from uuid import uuid4

import dotenv
import pandas
from genericpath import isfile
from numpy import PINF
from pydantic import StrictStr

from app.email_classifier import EmailClassifier
from app.models.common import PyObjectId
from app.models.email import Annotation, Email_Base

if dotenv.find_dotenv():
    print("Loading .env file")
    dotenv.load_dotenv(dotenv.find_dotenv())

path_dir_data = os.environ.get("PATH_DIR_DATASET_RAW")
if path_dir_data is None:
    raise ValueError("Please set PATH_DIR_DATASET_RAW")

path_dir_model_cache = os.environ.get("PATH_DIR_MODEL_CACHE")
if path_dir_model_cache is None:
    raise ValueError("Please set PATH_DIR_MODEL_CACHE")

path_file_data = os.path.join(path_dir_data, "tbbca", "20231023_wwt_tags.csv")
path_file_model = os.path.join(path_dir_model_cache, "email_model.pkl")

data_frame_data = pandas.read_csv(
    path_file_data, header=0, keep_default_na=False, dtype={"ID": str, "Tags": str, "Phone": str, "Message": str}
)

list_email = []
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
    if len(body["content"].strip()) == 0:
        continue
    received_time: datetime = datetime.strptime(row["Date"], "%Y-%m-%d %H:%M:%S")
    mailbox_id: PyObjectId = PyObjectId()
    tags = []
    if 0 < len(row["Tags"].strip()):
        tags.append(
            Annotation(
                annotation_id=str(uuid4()),
                source="csv",
                values={row["Tags"]: 1.0},
            )
        )
    dict_data = {
        "subject": subject,
        "body": body,
        "from_address": from_address,
        "received_time": received_time,
        "mailbox_id": mailbox_id,
        "tags": tags,
    }
    email = Email_Base(**dict_data)
    list_email.append(email)


classfier = EmailClassifier()
if os.path.isfile(path_file_model):
    classfier.load(path_file_model)
else:
    classfier.fit(list_email)
    classfier.save(path_file_model)
# count correct
count = 0
count_total = 0
for email in list_email:
    tag = classfier.predict_email_tags(email)
    # print(tag)
    if len(email.tags) == 0:
        continue
    else:
        count_total += 1
    if tag == list(email.tags[0].values.keys())[0]:
        count += 1


print(f"accuracy: {count/count_total}")
