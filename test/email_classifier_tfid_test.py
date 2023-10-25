import asyncio
import os

import dotenv
from email_test import read_emails

from app.email_classifier_tfid import EmailClassifierTfid

if dotenv.find_dotenv():
    dotenv.load_dotenv(dotenv.find_dotenv())

path_dir_model_cache = os.environ.get("PATH_DIR_MODEL_CACHE")
if path_dir_model_cache is None:
    raise ValueError("Please set PATH_DIR_MODEL_CACHE")

path_file_model = os.path.join(path_dir_model_cache, "email_model.pkl")
list_email = read_emails()


classfier = EmailClassifierTfid()
if os.path.isfile(path_file_model):
    classfier.load(path_file_model)
else:
    classfier.fit(list_email)
    classfier.save(path_file_model)
# count correct
count = 0
count_total = 0
for email in list_email:
    # print(tag)
    if len(email.annotations) == 0:
        continue
    else:
        count_total += 1

    label_pred = classfier.predict_email_tags(email)[0].label
    label_true = email.annotations[0].label
    if label_pred == label_true:
        count += 1


print(f"accuracy: {count/count_total}")


# asyncio.run(main())
