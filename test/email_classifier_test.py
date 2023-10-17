import os

import dotenv
from email_test import read_emails

from app.email_classifier import EmailClassifier

if dotenv.find_dotenv():
    dotenv.load_dotenv(dotenv.find_dotenv())

path_dir_model_cache = os.environ.get("PATH_DIR_MODEL_CACHE")
if path_dir_model_cache is None:
    raise ValueError("Please set PATH_DIR_MODEL_CACHE")

path_file_model = os.path.join(path_dir_model_cache, "email_model.pkl")
list_email = read_emails()


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
