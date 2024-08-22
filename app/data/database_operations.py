# -------------------------------------------------------------------------------
# Engineering
# operations.py
# -------------------------------------------------------------------------------
"""Async operations for the database"""
# -------------------------------------------------------------------------------
# Copyright (C) 2022 Array Insights, Inc. All Rights Reserved.
# Private and Confidential. Internal Use Only.
#     This software contains proprietary information which shall not
#     be reproduced or transferred to other documents and shall not
#     be disclosed to others for any purpose without
#     prior written permission of Array Insights, Inc.
# -------------------------------------------------------------------------------

import os
from typing import Any, Dict, List, Optional, Tuple

import motor.motor_asyncio
import pymongo.results as results
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from motor.core import AgnosticCursor
from pymongo.server_api import ServerApi

from app.models.email import Email_Db
from app.utils.secrets import get_secret


class DatabaseOperations:
    def __new__(cls):
        if cls._instance is None:
            # write the certificate to a tmp file
            with open("/tmp/mongo_atlas_cert.pem", "w") as f:
                credential = DefaultAzureCredential()
                client = SecretClient(vault_url=get_secret("DEVOPS_KEYVAULT_URL"), credential=credential)
                secret = client.get_secret("mongo-connection-certificate")
                if not secret.value:
                    raise Exception("Could not retrieve the secret")
                f.write(secret.value)

            cls._instance = super(DatabaseOperations, cls).__new__(cls)
            cls.mongodb_host = get_secret("MONGO_CONNECTION_URL")
            cls.client = motor.motor_asyncio.AsyncIOMotorClient(
                cls.mongodb_host, tls=True, tlsCertificateKeyFile="/tmp/mongo_atlas_cert.pem", server_api=ServerApi("1")
            )
            cls.sail_db = cls.client[get_secret("MONGO_DB_NAME")]

            # remove the certificate
            os.remove("/tmp/mongo_atlas_cert.pem")
        return cls._instance

    async def find_one(self, collection, query) -> Optional[dict]:
        return await self.sail_db[collection].find_one(query)

    async def find_many(
        self, collection: str, *, batch_size=1000, cursor: Optional[AgnosticCursor] = None
    ) -> Tuple[AgnosticCursor, List[Email_Db]]:
        if cursor is None:
            cursor = self.sail_db[collection].find()
        elif not cursor.alive:
            raise Exception("Cursor is not alive")

        return cursor, await cursor.to_list(batch_size)  # type: ignore

    async def find_all(self, collection: str, *, batch_size=1000) -> List[Email_Db]:
        cursor = self.sail_db[collection].find()
        list_all = []
        while cursor.alive:
            list_all.extend(await cursor.to_list(batch_size))
        list_all_email_db = []
        for email_dict in list_all:
            list_all_email_db.append(Email_Db(**email_dict))

        return list_all

    async def find_sorted(self, collection: str, query: Dict, sort_key: str, sort_direction: int) -> List[Email_Db]:
        return await self.sail_db[collection].find(query).sort(sort_key, sort_direction).to_list(1000)

    async def find_sorted_pagination(
        self,
        collection: str,
        query: Dict,
        sort_key: str,
        sort_direction: int,
        skip: int,
        limit: int,
    ) -> list:
        return (
            await self.sail_db[collection]
            .find(query)
            .sort(sort_key, sort_direction)
            .skip(skip)
            .limit(limit)
            .to_list(1000)
        )

    async def find_by_query(self, collection: str, query) -> List[Dict[str, Any]]:
        return await self.sail_db[collection].find(query).to_list(1000)

    async def insert_one(self, collection: str, data) -> results.InsertOneResult:
        return await self.sail_db[collection].insert_one(data)

    async def update_one(self, collection: str, query: dict, data) -> results.UpdateResult:
        return await self.sail_db[collection].update_one(query, data)

    async def update_many(self, collection: str, query: dict, data) -> results.UpdateResult:
        return await self.sail_db[collection].update_many(query, data)

    async def delete(self, collection: str, query: dict) -> results.DeleteResult:
        return await self.sail_db[collection].delete_one(query)

    async def drop(self):
        return await self.client.drop_database(self.sail_db)
