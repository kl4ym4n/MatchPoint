from aiohttp import web
from api.config_api import API_SETTINGS
from api.routes import setup_routes
from services import config
from services.dao.factory import DaoFactory


async def _close_factory(app: web.Application):
    await app["factory"].close()


async def _init_factory(app: web.Application):
    app["factory"] = DaoFactory(config.SETTINGS.POSTGRES_CONFIG.connection_string)


def init_app() -> web.Application:
    app = web.Application(client_max_size=1024 * 1000000)

    app.on_startup.extend([_init_factory])
    app.on_cleanup.extend([_close_factory])

    setup_routes(app)
    return app


if __name__ == "__main__":
    _app = init_app()
    web.run_app(_app, host=API_SETTINGS.SERVER_HOST, port=API_SETTINGS.SERVER_PORT)
