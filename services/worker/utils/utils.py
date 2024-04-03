import zipfile
import cv2
import numpy as np
import struct
import os
import shutil
from itertools import combinations
import wget


def get_filenames_in_directory(directory):
    filenames = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            filenames.append(os.path.join(root, file))
    return filenames


def match_and_count_matches(descriptors1, descriptors2, kp1, kp2):
    # Initialize feature matcher
    bf = cv2.BFMatcher()

    # Match descriptors
    des1 = np.array(descriptors1, dtype=np.float32)
    des2 = np.array(descriptors2, dtype=np.float32)
    matches = bf.knnMatch(cv2.UMat(des1), cv2.UMat(des2), k=2)

    # Apply ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.8 * n.distance:
            good_matches.append(m)

    mutual_matches = []
    for match in good_matches:
        reverse_match = next((m for m in good_matches if m.queryIdx == match.trainIdx and m.trainIdx == match.queryIdx),
                             None)
        if reverse_match:
            mutual_matches.append(match)

    # Count matches
    num_matches = len(mutual_matches)

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


def process_task(message):
    wget.download(message['url'], message['object'])

    extract_archive(message['object'], "temp")

    temp_name = "temp/" + message['object'].replace('.zip', '')

    filenames = get_filenames_in_directory(temp_name)

    file_pairs = list(combinations(filenames, 2))
    count = 0
    result = {}
    for pair in file_pairs:
        count += 1
        keypoints1, descriptors1 = read_binary_file(pair[0])
        keypoints2, descriptors2 = read_binary_file(pair[1])

        matches = match_and_count_matches(descriptors1, descriptors2, keypoints1, keypoints2)

        result[count] = f"Number of matches between {pair[0]} and {pair[1]}: {matches}"

    if os.path.exists(message['object']):
        os.remove(message['object'])
    if os.path.exists(temp_name):
        shutil.rmtree(temp_name)

    return result
