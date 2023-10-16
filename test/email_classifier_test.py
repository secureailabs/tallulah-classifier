import os

import dotenv
import pandas

from app.email_classifier import EmailClassifier
from app.models.email import Email_Base

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
classfier = EmailClassifier()
classfier.load(path_file_model)

data_frame_data = pandas.read_csv(
    path_file_data, header=0, keep_default_na=False, dtype={"ID": str, "Tags": str, "Phone": str, "Message": str}
)

classfier.predict_email_tags(Email_Base)
