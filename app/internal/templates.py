from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


def get_template_response(
    request: Request,
    name: str,
    context: dict | None = None
):
    if context is None:
        context = {}
    
    return templates.TemplateResponse(request=request, name=name, context=context)
