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
    UNPROCESSED = "UNPROCESSED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Annotation(SailBaseModel):
    annotation_id: StrictStr = Field()
    source: StrictStr = Field()
    values: Dict[str, float] = Field()


class Email_Base(SailBaseModel):
    subject: StrictStr = Field()
    body: Dict = Field()
    from_address: Dict = Field()
    received_time: datetime = Field()
    mailbox_id: PyObjectId = Field()
    annotations: List[Annotation] = Field(default=[])
    note: Optional[StrictStr] = Field(default=None)
    message_state: EmailState = Field(default=EmailState.UNPROCESSED)


class Email_Db(Email_Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_time: datetime = Field(default_factory=datetime.utcnow)
