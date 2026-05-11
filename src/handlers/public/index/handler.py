from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
templates = Jinja2Templates(directory=str(PROJECT_ROOT / 'templates'))

public_index_router = APIRouter()


@public_index_router.get('/')
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={},
    )
