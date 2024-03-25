
import typing as t
from pathlib import Path

import aiohttp
import aiohttp_cors
from aiohttp import web
from aiohttp.web_urldispatcher import UrlDispatcher

from api.config_api import API_SETTINGS
from api import views

BASE_PATH = Path(__file__).parent


def _redirect(redirect_url: str) -> t.Callable:
    async def redirect_handler(request):
        raise web.HTTPFound(redirect_url)

    return redirect_handler


def _add_routes(router: t.Union[UrlDispatcher]) -> None:
    router.add_route(
        "*", rf"{API_SETTINGS.URL_PREFIX}/tasks/{{task_id:\d+}}", views.TaskHandler
    )
    router.add_route("*", rf"{API_SETTINGS.URL_PREFIX}/tasks", views.TaskListHandler)


def setup_routes(app: web.Application) -> None:
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )

    router = app.router

    _add_routes(router)

    for route in list(app.router.routes()):
        cors.add(route, webview=True)
