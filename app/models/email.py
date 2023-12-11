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

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from numpy import source
from pydantic import Field, StrictStr

from app.models.common import PyObjectId, SailBaseModel


class EmailState(Enum):
    NEW = "NEW"
    TAGGED = "TAGGED"
    RESPONDED = "RESPONDED"
    FAILED = "FAILED"


class Annotation(SailBaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId)
    source: StrictStr = Field()
    label: StrictStr = Field()
    label_scores: Dict[str, float] = Field()


class Email_Base(SailBaseModel):
    subject: Optional[StrictStr] = Field(default=None)
    body: Optional[Dict] = Field(default_factory=dict)
    from_address: Dict = Field()
    received_time: str = Field()
    mailbox_id: PyObjectId = Field()
    user_id: PyObjectId = Field()
    label: Optional[StrictStr] = Field(default=None)
    annotations: List[Annotation] = Field(default=[])
    note: Optional[StrictStr] = Field(default=None)
    message_state: EmailState = Field(default=EmailState.NEW)
    outlook_id: StrictStr = Field()

    def get_annotation(self, source: str) -> Optional[Annotation]:
        for annotation in self.annotations:
            if annotation.source == source:
                return annotation
        return None


class Email_Db(Email_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
