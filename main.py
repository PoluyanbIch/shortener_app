from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
import validators
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import SessionLocal, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


def raise_not_found(request):
    message = f'URL "{request.url}" does not exist'
    raise HTTPException(status_code=404, detail=message)


@app.get('/')
def read_root():
    return 'Welcome to the URL shortener API'


@app.post('/url', response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Annotated[Session, Depends(get_db)]):
    if not validators.url(url.target_url.unicode_string()):
        raise_bad_request(message='Your provided URL is not valid')

    db_url = crud.add_db_url(db, url)

    db_url.url = db_url.key
    db_url.admin_url = db_url.secret_key

    return db_url


@app.get('/{url_key}')
def forward_to_target_url(url_key: str, request: Request, db: Annotated[Session, Depends(get_db)]):
    if db_url := crud.get_db_url_by_key(db, url_key):
        return RedirectResponse(db_url.target_url)
    raise_not_found(request)
