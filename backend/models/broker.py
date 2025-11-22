# ===================================
# models/broker.py (Support for broker/server management)
# ===================================
from pydantic import BaseModel
from typing import List

class Server(BaseModel):
    server_name: str
    server_address: str
    status: str = "active"

class Broker(BaseModel):
    broker_name: str
    servers: List[Server]
    status: str = "active"

class BrokerResponse(BaseModel):
    brokers: List[Broker]