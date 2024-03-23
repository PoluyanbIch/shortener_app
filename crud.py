from sqlalchemy.orm import Session

from . import keygen, models, schemas


def add_db_url(db: Session, url: schemas.URLBase) -> models.URL:
    key = keygen.create_unique_random_key()
    secret_key = keygen.create_random_key(8)
    db_url = models.URL(
        key=key,
        secret_key=secret_key,
        target_url=url.target_url
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_db_url_by_key(db: Session, url_key: str) -> models.URL | None:
    return db.query(models.URL).filter(models.URL.key == url_key, models.URL.is_active).first()

