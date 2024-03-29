import asyncio
import json
from itertools import combinations
from aio_pika import connect, Message
from services import config
from minio import Minio
from services import dto
from services.dao.factory import DaoFactory
import utils
from services.task_service.api.exceptions import NotFoundException
from sqlalchemy.dialects.postgresql import JSONB

minio_client = Minio(config.SETTINGS.MINIO_CONFIG.MINIO_HOST + ":" + config.SETTINGS.MINIO_CONFIG.MINIO_PORT,
                     access_key=config.SETTINGS.MINIO_CONFIG.MINIO_ACCESS_KEY,
                     secret_key=config.SETTINGS.MINIO_CONFIG.MINIO_SECRET_KEY,
                     secure=False)


async def callback(message: Message):
    async with message.process():

        factory: DaoFactory = DaoFactory(config.SETTINGS.POSTGRES_CONFIG.connection_string)
        try:
            decoded_message = json.loads(message.body.decode())
            print(decoded_message)
            async with factory.session_maker() as session:
                task_dao = await factory.create_task_dao(session)
                task_data = dto.TaskDTO(**{"status": dto.TaskStatus.RUNNING})
                task = await task_dao.update(decoded_message.id, task_data)
                if task is None:
                    raise NotFoundException(f"Task with id {decoded_message.id} does not exist")
                await session.commit()

            try:
                response = minio_client.get_object(config.SETTINGS.MINIO_CONFIG.MINIO_BUCKET, decoded_message.object)
                utils.extract_archive(response, "temp")
            finally:
                response.close()
                response.release_conn()

            filenames = utils.get_filenames_in_directory("temp/" + decoded_message.object)

            file_pairs = list(combinations(filenames, 2))
            # for pair in file_pairs:
            #     keypoints1, descriptors1 = utils.read_binary_file(pair[0])
            #     keypoints2, descriptors2 = utils.read_binary_file(pair[1])
            #
            #     matches = utils.match_and_count_matches(descriptors1, descriptors2)
            #
            #     print(f"Number of matches between {pair[0]} and {pair[1]}: {matches}")

        except Exception as err:

            async with factory.session_maker() as session:
                task_dao = await factory.create_task_dao(session)
                task_data = dto.TaskDTO(**{"status": dto.TaskStatus.ERROR, "id": decoded_message['id'],  "result": json.dumps({"error": str(err)})})
                await task_dao.update(decoded_message['id'], task_data)
                await session.commit()


async def main():
    connection = await connect(config.SETTINGS.RABBIT_CONFIG.connection_string)
    channel = await connection.channel()
    queue = await channel.declare_queue(config.SETTINGS.QUEUE_NAME)

    await queue.consume(callback)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
