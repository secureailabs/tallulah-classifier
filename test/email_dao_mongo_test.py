import asyncio

# Importing custom module
from app.email_dao_mongo import EmailDaoMongo
from app.models.common import PyObjectId
from app.models.email import Annotation, Email_Base, EmailState


async def main():
    # Initialize an instance of EmailDaoMongo for MongoDB connection
    email_dao = EmailDaoMongo("mongodb://127.0.0.1:27017", "tallulah", "emails_temp")

    # Delete all existing emails in the database
    await email_dao.delete_all()
    result = await email_dao.read_all()
    print(len(result))

    # Create a test email and add it to the database
    result = await email_dao.create(
        Email_Base(
            mailbox_id=PyObjectId(),
            subject="test",
            body={},
            received_time="",
            from_address={},
            message_state=EmailState.NEW,
            annotations=[],
            outlook_id="test",
            user_id=PyObjectId(),
        )
    )

    # Read all emails from the database and print the count
    result = await email_dao.read_all()
    print(len(result))

    # Get the ID of the created test email
    email_id = result[0].id

    # Read the test email and print the initial count of annotations
    result = await email_dao.read(email_id)
    print(len(result[0].annotations))

    # Add an annotation to the test email and print the updated count
    await email_dao.add_annotation(email_id, Annotation(source="test", label="test", label_scores={"test": 0.5}))
    result = await email_dao.read(email_id)
    print(len(result[0].annotations))

    # Add another annotation to the test email and print the updated count
    await email_dao.add_annotation(email_id, Annotation(source="test", label="test2", label_scores={"test": 0.5}))
    result = await email_dao.read(email_id)
    print(len(result[0].annotations))

    # Add an annotation with a different source to the test email and print the updated count
    await email_dao.add_annotation(email_id, Annotation(source="test2", label="test", label_scores={"test": 0.5}))
    result = await email_dao.read(email_id)
    print(len(result[0].annotations))

    # Delete all existing emails in the database
    await email_dao.delete_all()


if __name__ == "__main__":
    # Run the asynchronous main function using asyncio
    asyncio.run(main())
