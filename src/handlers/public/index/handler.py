from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates

from core.paths import bundle_root

templates = Jinja2Templates(directory=str(bundle_root() / 'templates'))

public_index_router = APIRouter()


@public_index_router.get('/')
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={},
    )
