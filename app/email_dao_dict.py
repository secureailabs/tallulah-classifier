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
from uuid import uuid4

from app.email_dao_base import EmailDaoBase
from app.models.common import PyObjectId
from app.models.email import Annotation, Email_Base, Email_Db, EmailState


class EmailDaoDict(EmailDaoBase):
    def __init__(self):
        self.dict_email = {}

    async def create(
        self,
        email: Email_Base,
    ) -> str:
        email_id = str(uuid4())
        email_data = email.dict()
        email_data["_id"] = email_id

        self.dict_email[email_id] = Email_Db(**email_data)
        return email_id

    async def read(
        self,
        email_id: PyObjectId,
        throw_on_not_found: bool = True,
    ) -> Optional[Email_Db]:
        if str(email_id) in self.dict_email:
            return self.dict_email[str(email_id)]
        if throw_on_not_found:
            raise RuntimeError(f"Email not found for id: {email_id}")
        else:
            return None

    async def update(
        self,
        query_message_id: Optional[PyObjectId] = None,
        update_message_state: Optional[EmailState] = None,
        update_message_annotations: Optional[List[Annotation]] = None,
    ):
        pass
