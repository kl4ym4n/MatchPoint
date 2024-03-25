import asyncio
import zipfile
import os
import cv2
import numpy as np
import struct
from itertools import combinations
from aio_pika import connect, Message


async def callback(message: Message):
    async with message.process():
        extract_archive("kpts.zip", "temp")
        filenames = get_filenames_in_directory("temp/kpts")

        file_pairs = list(combinations(filenames, 2))
        for pair in file_pairs:
            keypoints1, descriptors1 = read_binary_file(pair[0])
            keypoints2, descriptors2 = read_binary_file(pair[1])

            matches = match_and_count_matches(descriptors1, descriptors2)

            print(f"Number of matches between {pair[0]} and {pair[1]}: {matches}")

        print(f"Received message: {message.body.decode()}")


def get_filenames_in_directory(directory):
    filenames = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            filenames.append(os.path.join(root, file))
    return filenames


def match_and_count_matches(descriptors1, descriptors2):
    # Initialize feature matcher
    bf = cv2.BFMatcher()

    # Match descriptors
    des1 = np.array(descriptors1, dtype=np.float32)
    des2 = np.array(descriptors2, dtype=np.float32)
    matches = bf.knnMatch(cv2.UMat(des1), cv2.UMat(des2), k=2)

    # Count matches
    num_matches = len(matches)

    return num_matches


def read_binary_file(file_path):
    with open(file_path, "rb") as file:
        content = file.read()
        num_keypoints = struct.unpack("<I", content[:4])[0]
        descriptor_size = struct.unpack("<I", content[4:8])[0]

        keypoints = []
        descriptors = []

        for i in range(num_keypoints):
            index = 8 + i * (28 + descriptor_size * 4)
            keypoint_data = struct.unpack_from("<ffffffif", content, index)

            keypoints.append(keypoint_data[:8])
            descriptor_bytes = struct.unpack_from("<" + "f" * descriptor_size, content, index + 28)
            descriptors.append(descriptor_bytes)

        return keypoints, descriptors


def extract_archive(archive_path, extract_dir):
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
        print(f"Archive extracted to {extract_dir}")


async def main():
    connection = await connect('amqp://guest:guest@rabbitmq/')
    channel = await connection.channel()
    queue = await channel.declare_queue('task_queue')

    await queue.consume(callback)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
