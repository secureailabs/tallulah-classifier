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

import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from data import operations as data_service
from models.common import PyObjectId, SailBaseModel
from pydantic import EmailStr, Field, StrictStr


class EmailState(Enum):
    UNPROCESSED = "UNPROCESSED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Email_Base(SailBaseModel):
    subject: StrictStr = Field()
    body: Dict = Field()
    from_address: Dict = Field()
    received_time: datetime = Field()
    mailbox_id: PyObjectId = Field()
    tags: List[StrictStr] = Field(default=[])
    note: Optional[StrictStr] = Field(default=None)
    message_state: EmailState = Field(default=EmailState.UNPROCESSED)


class Email_Db(Email_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)


class Emails:
    DB_COLLECTION_EMAILS = "emails"

    @staticmethod
    async def read(
        email_id: Optional[PyObjectId] = None,
        throw_on_not_found: bool = True,
    ) -> List[Email_Db]:
        messages_list = []

        query = {}
        if email_id:
            query["_id"] = str(email_id)

        response = await data_service.find_by_query(
            collection=Emails.DB_COLLECTION_EMAILS,
            query=query,
        )

        if response:
            for data_model in response:
                messages_list.append(Email_Db(**data_model))
        elif throw_on_not_found:
            raise Exception(f"No messages found for query: {query}")

        return messages_list

    @staticmethod
    async def update(
        query_message_id: Optional[PyObjectId] = None,
        update_message_state: Optional[EmailState] = None,
        update_message_tags: Optional[List[str]] = None,
    ):
        query = {}
        if query_message_id:
            query["_id"] = str(query_message_id)

        update_request = {"$set": {}}
        if update_message_state:
            update_request["$set"]["message_state"] = update_message_state.value
        if update_message_tags:
            update_request["$set"]["tags"] = update_message_tags

        update_response = await data_service.update_many(
            collection=Emails.DB_COLLECTION_EMAILS,
            query=query,
            data=update_request,
        )

        if update_response.modified_count == 0:
            raise Exception(f"Email not found or no changes to update")
