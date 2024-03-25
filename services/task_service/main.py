from aiohttp import web

from api.config_api import API_SETTINGS
from api.routes import setup_routes
from config import SETTINGS
from dao.factory import DaoFactory


# async def healthcheck(request):
#     return web.Response(text="Working!")
#
#
# async def tasks(request):
#     session = Session()
#     all_tasks = session.query(Task).all()
#     results = [{'id': task.id, 'filename': task.filename, 'status': task.status} for task in all_tasks]
#     json_data = json.dumps(results, default=str)
#     return web.json_response({'data': json_data})
#
#
# async def create_task(request):
#     filename = request.query.get('filename')
#     description = request.query.get('description')
#
#     connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
#     channel = connection.channel()
#
#     channel.queue_declare(queue='task_queue')
#
#     channel.basic_publish(exchange='', routing_key='task_queue', body='Hello, RabbitMQ!')
#
#     connection.close()
#
#     session = Session()
#     new_task = Task(filename=filename, description=description, status='NEW')
#     session.add(new_task)
#     result = {'filename': new_task.filename, 'status': new_task.status}
#     session.commit()
#     session.close()
#
#     return web.json_response({'data': result})
#
#
# app = web.Application()
# app.add_routes([web.get('/', healthcheck)])
# app.add_routes([web.get('/tasks', tasks)])
# app.add_routes([web.get('/createTask', create_task)])
# web.run_app(app)

async def _close_factory(app: web.Application):
    await app["factory"].close()


async def _init_factory(app: web.Application):
    app["factory"] = DaoFactory(SETTINGS.POSTGRES_CONFIG.connection_string)


def init_app() -> web.Application:
    app = web.Application(client_max_size=1024*50000)

    app.on_startup.extend([_init_factory])
    app.on_cleanup.extend([_close_factory])

    setup_routes(app)
    return app


if __name__ == "__main__":
    _app = init_app()
    web.run_app(_app, host=API_SETTINGS.SERVER_HOST, port=API_SETTINGS.SERVER_PORT)
