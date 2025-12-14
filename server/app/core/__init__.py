"""
Core module initialization.
"""
from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.core.logging import setup_logging, logger
from app.core.email import email_service
from app.core import exceptions

__all__ = [
    'settings',
    'Base',
    'engine',
    'get_db',
    'setup_logging',
    'logger',
    'email_service',
    'exceptions'
]
