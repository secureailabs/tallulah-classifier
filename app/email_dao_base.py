from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.common import PyObjectId
from app.models.email import Annotation, Email_Base, Email_Db, EmailState


class EmailDaoBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def create(
        self,
        email: Email_Base,
    ) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def read(
        self,
        email_id: PyObjectId,
        throw_on_not_found: bool = True,
    ) -> List[Email_Db]:
        raise NotImplementedError()

    @abstractmethod
    async def update(
        self,
        query_message_id: Optional[PyObjectId] = None,
        update_message_state: Optional[EmailState] = None,
        update_message_annotations: Optional[List[Annotation]] = None,
    ):
        raise NotImplementedError()
