from typing import Annotated

import validators
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.events import GoToEvent
from fastui.forms import fastui_form
from sqlalchemy.orm import Session

import crud
import models
import schemas
from config import get_settings
from database import SessionLocal, engine

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


@app.get("/api/", response_model=FastUI, response_model_exclude_none=True)
def read_root(url: str | None = None) -> list[AnyComponent]:
    components = [
        c.Heading(text='Short your URL', level=1),
        c.ModelForm(model=schemas.Model, submit_url='/url')
    ]

    if url is not None:
        components += [
            c.Heading(text="Your shorten URL!", level=1),
            c.Link(components=[c.Text(text=url)], on_click=GoToEvent(url=f'{get_settings().base_url}/{url}'))
        ]
    print(components)
    return [c.Page(components=components)]


@app.post('/url')
def create_url(url: Annotated[schemas.Model, fastui_form(schemas.Model)], db: Annotated[Session, Depends(get_db)]):
    url = schemas.URLBase(target_url=url.url)
    if not validators.url(url.target_url):
        raise_bad_request(message='Your provided URL is not valid')

    db_url = crud.add_db_url(db, url)

    db_url.url = db_url.key
    db_url.admin_url = db_url.secret_key

    return [c.FireEvent(event=GoToEvent(url=f'/api/new_link/', query={'url': db_url.url}))]


@app.get('/{url_key}')
def forward_to_target_url(url_key: str, request: Request, db: Annotated[Session, Depends(get_db)]):
    if db_url := crud.get_db_url_by_key(db, url_key):
        crud.update_db_clicks(db, db_url)
        return RedirectResponse(db_url.target_url)
    raise_not_found(request)


@app.get('/admin/{secret_key}', name='administration info', response_model=schemas.URLInfo)
def get_url_info(secret_key: str, request: Request, db: Annotated[Session, Depends(get_db)]):
    if db_url := crud.get_db_url_by_secret_key(db, secret_key):
        db_url.url = db_url.key
        db_url.admin_url = db_url.secret_key
        return db_url
    raise_not_found(request)


@app.delete('/admin/{secret_key}')
def delete_url(secret_key: str, request: Request, db: Annotated[Session, Depends(get_db)]):
    if url := crud.delete_db_url_by_secret_key(db=db, secret_key=secret_key):
        message = f'Successfully deleted shortener URL for "{url}"'
        return {'detail': message}
    raise_not_found(request)


@app.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title='URL Shortener'))
