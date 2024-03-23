from sqlalchemy.orm import Session

from . import keygen, models, schemas


def add_db_url(db: Session, url: schemas.URLBase) -> models.URL:
    key = keygen.create_unique_random_key(db=db)
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


def get_db_url_by_secret_key(db: Session, secret_key: str) -> models.URL | None:
    return db.query(models.URL).filter(models.URL.secret_key == secret_key, models.URL.is_active).first()


def update_db_clicks(db: Session, db_url: schemas.URL) -> models.URL:
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url


def delete_db_url_by_secret_key(db: Session, secret_key: str) -> str:
    if db_url := get_db_url_by_secret_key(db=db, secret_key=secret_key):
        db_url.is_active = False
        url = db_url.target_url
        db.delete(db_url)
        db.commit()
        return url
