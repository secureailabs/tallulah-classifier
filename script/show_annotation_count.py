import asyncio
from typing import Dict, List
from uuid import uuid4

# Importing custom module
from app.email_dao_mongo import EmailDaoMongo
from app.models.email import Annotation


async def main():
    # Initialize an instance of EmailDaoMongo for MongoDB connection
    email_dao = EmailDaoMongo("mongodb://127.0.0.1:27017", "tallulah", "emails_temp")

    # Read all emails from the database
    list_email = await email_dao.read_all()

    # Create a dictionary to store annotations grouped by source
    dict_annotation: Dict[str, List[Annotation]] = {}

    # Iterate through each email and collect annotations by source
    for email in list_email:
        for annotation in email.annotations:
            if annotation.source not in dict_annotation:
                dict_annotation[annotation.source] = []
            dict_annotation[annotation.source].append(annotation)

    # Print the count of each annotation label for each source
    for source, list_annotation in dict_annotation.items():
        print(f"Source {source}")
        dict_count = {}
        for annotation in list_annotation:
            if annotation.label not in dict_count:
                dict_count[annotation.label] = 0
            dict_count[annotation.label] += 1
        for label, count in dict_count.items():
            print(f"-- {label}: {count}")


if __name__ == "__main__":
    # Run the asynchronous main function using asyncio
    asyncio.run(main())
