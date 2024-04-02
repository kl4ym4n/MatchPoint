import asyncio
import json
import os
import shutil
from aio_pika import connect, Message

import utils
from services import config
from services import dto
from handlers.base import BaseTaskHandler
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()


async def callback(message: Message):
    async with message.process():

        try:
            decoded_message = json.loads(message.body.decode())

            task_handler = BaseTaskHandler(config.SETTINGS.POSTGRES_CONFIG.connection_string)
            await task_handler.update_task({"task_id": decoded_message['id'], "status": dto.TaskStatus.RUNNING})

            result = await asyncio.get_event_loop().run_in_executor(executor, utils.process_task, decoded_message)

            await task_handler.update_task(
                {"task_id": decoded_message['id'], "status": dto.TaskStatus.COMPLETED,
                 "result": json.dumps(result)})

        except Exception as err:

            await task_handler.update_task(
                {"task_id": decoded_message['id'], "status": dto.TaskStatus.ERROR, "result": err})

            temp_name = "temp/" + message['object'].replace('.zip', '')
            if os.path.exists(message['object']):
                os.remove(message['object'])
            if os.path.exists(temp_name):
                shutil.rmtree(temp_name)


async def main():
    connection = await connect(config.SETTINGS.RABBIT_CONFIG.connection_string)

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(config.SETTINGS.QUEUE_NAME)

    await queue.consume(callback)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
