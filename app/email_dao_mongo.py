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

from app.data.database_operations import DatabaseOperations
from app.email_dao_base import EmailDaoBase
from app.models.common import PyObjectId
from app.models.email import Annotation, Email_Db, EmailState


class EmailDaoMongo(EmailDaoBase):
    DB_COLLECTION_EMAILS = "emails"

    def __init__(self):
        self.database_operations = DatabaseOperations()

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
            collection=EmailDaoMongo.DB_COLLECTION_EMAILS,
            query=query,
        )

        if response:
            for data_model in response:
                messages_list.append(Email_Db(**data_model))
        elif throw_on_not_found:
            raise Exception(f"No messages found for query: {query}")

        return messages_list

    async def update(
        self,
        query_message_id: Optional[PyObjectId] = None,
        update_message_state: Optional[EmailState] = None,
        update_message_annotations: Optional[Annotation] = None,
    ):
        query = {}
        if query_message_id:
            query["_id"] = str(query_message_id)

        update_request = {"$set": {}}
        if update_message_state:
            update_request["$set"]["message_state"] = update_message_state.value
        if update_message_annotations:
            update_request["$set"]["tags"] = update_message_annotations

        update_response = await self.database_operations.update_many(
            collection=EmailDaoMongo.DB_COLLECTION_EMAILS,
            query=query,
            data=update_request,
        )

        if update_response.modified_count == 0:
            raise Exception(f"Email not found or no changes to update")
