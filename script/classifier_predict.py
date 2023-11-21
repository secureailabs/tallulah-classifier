import asyncio
import os

import dotenv

from app.email_classifier_tfid import EmailClassifierTfid
from app.email_dao_mongo import EmailDaoMongo
from app.utils.secrets import get_secret


# Define an asynchronous main function
async def main():
    # Check if a .env file exists and load its contents into environment variables
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    # Initialize an instance of EmailDaoMongo for MongoDB connection
    email_dao = EmailDaoMongo("mongodb://127.0.0.1:27017", "tallulah", "emails_temp")

    # Read all emails from the database
    list_email = await email_dao.read_all()

    # Get the file path for the email classifier model from a secret
    path_file_model = get_secret("path_file_model")

    # Initialize an instance of EmailClassifierTfid
    classfier = EmailClassifierTfid()

    # Check if the model file exists, and if so, load the model
    if os.path.isfile(path_file_model):
        classfier.load(path_file_model)

    # Iterate through each email and predict its annotation using the classifier
    for email in list_email:
        annotation = classfier.predict_email_tags(email)[0]

        # Add the predicted annotation to the email in the database
        await email_dao.add_annotation(email.id, annotation)


# Run the main function when the script is executed
if __name__ == "__main__":
    asyncio.run(main())
