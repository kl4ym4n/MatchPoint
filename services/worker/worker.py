import asyncio
import json
import os
import shutil
from itertools import combinations

import wget
from aio_pika import connect, Message

import utils
from services import config
from services import dto
from handlers.base import BaseTaskHandler


async def callback(message: Message):
    async with message.process():

        try:
            decoded_message = json.loads(message.body.decode())

            task_handler = BaseTaskHandler(config.SETTINGS.POSTGRES_CONFIG.connection_string)
            await task_handler.update_task({"task_id": decoded_message['id'], "status": dto.TaskStatus.RUNNING})

            wget.download(decoded_message['url'], decoded_message['object'])

            utils.extract_archive(decoded_message['object'], "temp")

            temp_name = "temp/" + decoded_message['object'].replace('.zip', '')

            filenames = utils.get_filenames_in_directory(temp_name)

            file_pairs = list(combinations(filenames, 2))
            json_res = {}
            count = 0
            for pair in file_pairs:
                count += 1
                keypoints1, descriptors1 = utils.read_binary_file(pair[0])
                keypoints2, descriptors2 = utils.read_binary_file(pair[1])

                matches = utils.match_and_count_matches(descriptors1, descriptors2)

                json_res[count] = f"Number of matches between {pair[0]} and {pair[1]}: {matches}"

            await task_handler.update_task(
                {"task_id": decoded_message['id'], "status": dto.TaskStatus.RUNNING, "result": 'json.dumps(json_res)'})

            if os.path.exists(decoded_message['object']):
                os.remove(decoded_message['object'])
            if os.path.exists(temp_name):
                shutil.rmtree(temp_name)



        except Exception as err:

            await task_handler.update_task(
                {"task_id": decoded_message['id'], "status": dto.TaskStatus.ERROR})


async def main():
    connection = await connect(config.SETTINGS.RABBIT_CONFIG.connection_string)

    channel = await connection.channel()
    queue = await channel.declare_queue(config.SETTINGS.QUEUE_NAME)

    await queue.consume(callback)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
