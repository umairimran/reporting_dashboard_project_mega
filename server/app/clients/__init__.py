"""
Client management module initialization.
"""
from app.clients.models import Client, ClientSettings
from app.clients.schemas import (
    ClientCreate, ClientUpdate, ClientResponse, 
    ClientSettingsCreate, ClientSettingsResponse
)
from app.clients.service import ClientService
from app.clients.router import router

__all__ = [
    'Client',
    'ClientSettings',
    'ClientCreate',
    'ClientUpdate',
    'ClientResponse',
    'ClientSettingsCreate',
    'ClientSettingsResponse',
    'ClientService',
    'router'
]
