import urllib
import os
import cv2
import numpy as np

from . import settings

IMAGES_FOLDER = os.path.join(settings.BASE_DIR, "images")

CAMERA_SHOT_URL = settings.CAMERA_URL + '/shot.jpg'
CAMERA_IMAGE_PATH = os.path.join(IMAGES_FOLDER, "camera.jpg")
YOLO_IMAGE_PATH = os.path.join(IMAGES_FOLDER, "yolo.jpg")

def get_camera_image():
    resp = urllib.request.urlopen(CAMERA_SHOT_URL)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    return cv2.imdecode(image, cv2.IMREAD_COLOR)

def download_camera_image():
    urllib.urlretrieve(CAMERA_SHOT_URL, CAMERA_IMAGE_PATH)

def open_image(filename):
    image_path = os.path.join(IMAGES_FOLDER, filename)
    return cv2.imread(image_path, 0)

def store_image(image, filename):
    image_path = os.path.join(IMAGES_FOLDER, filename)
    cv2.imwrite(image_path, image)
