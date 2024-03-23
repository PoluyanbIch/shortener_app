import secrets
from string import ascii_uppercase

from sqlalchemy.orm import Session

from . import crud


def create_random_key(length: int = 5) -> str:
    return ''.join(secrets.choice(ascii_uppercase) for _ in range(length))


def create_unique_random_key(db: Session, length: int = 5) -> str:
    key = create_random_key(length)
    while crud.get_db_url_by_key(db, key):
        key = create_random_key(length)
    return key
