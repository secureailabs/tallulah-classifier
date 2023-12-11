# -------------------------------------------------------------------------------
# Engineering
# accounts.py
# -------------------------------------------------------------------------------
"""Models used by account management service"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Array Insights, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Array Insights, Inc.
# -------------------------------------------------------------------------------

from typing import Dict, List, Optional

from fastapi.encoders import jsonable_encoder

from app.data.database_operations import DatabaseOperations
from app.email_dao_base import EmailDaoBase
from app.models.common import PyObjectId
from app.models.email import Annotation, Email_Base, Email_Db, EmailState


class EmailDaoMongo(EmailDaoBase):
    def __init__(self, connection_string, database_name: str, collection_name: str):
        self.database_operations = DatabaseOperations(connection_string, database_name)
        self.collection_name = collection_name

    async def create(
        self,
        email: Email_Base,
    ) -> PyObjectId:
        email_db = Email_Db(
            mailbox_id=email.mailbox_id,
            subject=email.subject,
            body=email.body,
            received_time=email.received_time,
            from_address=email.from_address,
            message_state=email.message_state,
            annotations=email.annotations,
            outlook_id=email.outlook_id,
            user_id=email.user_id,
        )
        response = await self.database_operations.insert_one(
            collection=self.collection_name,
            data=jsonable_encoder(email_db),
        )
        if not response.acknowledged:
            raise Exception(f"Failed to insert email: {email}")
        return email_db.id

    async def read(
        self,
        email_id: PyObjectId,
        throw_on_not_found: bool = True,
    ) -> List[Email_Db]:
        messages_list = []

        query = {}
        if email_id:
            query["_id"] = str(email_id)

        response = await self.database_operations.find_by_query(
            collection=self.collection_name,
            query=query,
        )

        if response:
            for data_model in response:
                messages_list.append(Email_Db(**data_model))
        elif throw_on_not_found:
            raise Exception(f"No messages found for query: {query}")

        return messages_list

    async def read_all(
        self,
    ) -> List[Email_Db]:
        messages_list = []

        response = await self.database_operations.find_all(
            collection=self.collection_name,
        )

        if response:
            for email in response:
                messages_list.append(email)

        return messages_list

    async def update(
        self,
        query_message_id: Optional[PyObjectId] = None,
        update_message_state: Optional[EmailState] = None,
        update_message_annotations: Optional[List[Annotation]] = None,
    ):
        query = {}
        if query_message_id:
            query["_id"] = str(query_message_id)

        update_request = {"$set": {}}
        if update_message_state:
            update_request["$set"]["message_state"] = update_message_state.value
        if update_message_annotations:
            update_request["$set"]["annotations"] = update_message_annotations

        update_response = await self.database_operations.update_many(
            collection=self.collection_name,
            query=query,
            data=jsonable_encoder(update_request),
        )

        if update_response.modified_count == 0:
            raise Exception(f"Email not found or no changes to update")

    async def add_annotation(
        self,
        email_id: PyObjectId,
        annotation: Annotation,
    ):
        email = await self.read(email_id=email_id)
        email = email[0]
        # remove any existing annotation with the same source
        email.annotations = [a for a in email.annotations if a.source != annotation.source]

        query = {}
        if email_id:
            query["_id"] = str(email_id)

        update_request = {"$set": {}}

        # Update the display label it's not already set
        if email.label is None:
            update_request["$set"]["label"] = annotation.label
        update_request["$set"]["annotations"] = email.annotations
        update_request["$set"]["annotations"].append(annotation)
        update_response = await self.database_operations.update_many(
            collection=self.collection_name,
            query=query,
            data=jsonable_encoder(update_request),
        )

        if update_response.modified_count == 0:
            raise Exception(f"Email not found or no changes to update")

    async def delete_all(self) -> None:
        await self.database_operations.drop()
