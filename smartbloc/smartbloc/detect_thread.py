import threading
import os
import time

import numpy as np
import cv2

from . import yolo
from . import settings
from . import image_lib

DETECT_THREAD_PERIOD_MS = 1000
LABELS_PATH = os.path.join(settings.BASE_DIR, "yolo-coco/coco.names")
WEIGHTS_PATH = os.path.join(settings.BASE_DIR, "yolo-coco/yolov3.weights")
CONFIG_PATH = os.path.join(settings.BASE_DIR, "yolo-coco/yolov3.cfg")

LABELS = open(LABELS_PATH).read().strip().split("\n")

CONFIDENCE = 0.5
THRESHOLD = 0.3

np.random.seed(int(time.time()))
COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")

current_detect_thread = None

class DetectThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        self.remaining_trials = 5

        self.top_reached = False
        self.done = False

        self.start_time = 0
        self.end_time = 0
        self.duration = 0
    
    def step(self):
        img = image_lib.get_camera_image()
        (h, w) = img.shape[0:2]

        image_lib.store_image(img, image_lib.CAMERA_IMAGE_PATH)

        (boxes, confidences, class_ids) = yolo.yolo_image(CONFIG_PATH, WEIGHTS_PATH,
            image_lib.CAMERA_IMAGE_PATH, CONFIDENCE, THRESHOLD)
        
        box_labels = [LABELS[i] for i in class_ids]
        box_colors = [COLORS[i].tolist() for i in class_ids]

        # Detect if climber is done
        if self.climber_is_on_top(boxes, confidences, box_labels):
            print("[DETECT THREAD] Top reached !")
            self.top_reached = True
        
        if self.climber_is_on_bottom(h, boxes, confidences, box_labels):
            print("[DETECT THREAD] Bottom reached !")
            if self.top_reached:
                print("[DETECT THREAD] Done !")
                self.done = True
                self.running = False

        # Draw boxes on image
        yolo.draw_boxes_on_image(img, boxes, box_labels, box_colors, confidences)
        
        # Draw margins on image
        cv2.rectangle(img, (0, 0), (w, settings.CAMERA_MARGIN_TOP), (255, 0, 0), 2)
        cv2.rectangle(img, (0, h - settings.CAMERA_MARGIN_BOTTOM), (w, h), (255, 0, 0), 2)

        image_lib.store_image(img, image_lib.YOLO_IMAGE_PATH)

    def loop(self):        
        print("[DETECT THREAD] Running...")
        loop_start_time = time.time()

        try:
            self.step()

            # If step is successful, reset self.remaining_trials
            self.remaining_trials = 5
        except OSError as e:
            print("[DETECT THREAD] [ERROR] Camera not available: ", e)

            if self.remaining_trials <= 0:
                print("[DETECT THREAD] ABORTING THREAD AFTER 5 ATTEMPS")
                return
            
            self.remaining_trials -= 1        

        loop_end_time = time.time()
        loop_duration = loop_end_time - loop_start_time
        print("[DETECT THREAD] Loop duration: {:.6f}".format(loop_duration))

        if not self.running:
            return
        
        if loop_duration < DETECT_THREAD_PERIOD_MS:
            time.sleep(float(DETECT_THREAD_PERIOD_MS - loop_duration) / 1000.0)
        
        self.loop()

    def run(self):
        self.start_time = time.time()
        
        self.loop()

        self.running = False

        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def climber_is_on_top(self, boxes, confidences, labels):
        for i in range(len(boxes)):
            if labels[i] == 'person':
                (_, y) = (boxes[i][0], boxes[i][1])
                (_, h) = (boxes[i][2], boxes[i][3])

                print("[DETECT THREAD] Person found at {} with height of {}".format(y, h))
                if y <= settings.CAMERA_MARGIN_TOP:
                    return True

    def climber_is_on_bottom(self, img_height, boxes, confidences, labels):
        for i in range(len(boxes)):
            if labels[i] == 'person':
                (_, y) = (boxes[i][0], boxes[i][1])
                (_, h) = (boxes[i][2], boxes[i][3])

                if y + h >= img_height - settings.CAMERA_MARGIN_BOTTOM:
                    return True

def create_new_thread():
    global current_detect_thread

    if current_detect_thread is not None:
        print("done:", current_detect_thread.done)
        print("running:", current_detect_thread.running)

        current_detect_thread.running = False
        current_detect_thread.join()
    
    current_detect_thread = DetectThread()
    current_detect_thread.start()

def get_status():
    global current_detect_thread

    if current_detect_thread is None:
        return 'waiting'
    if current_detect_thread.running:
        return 'running'
    if current_detect_thread.done:
        return 'done'
    return 'failed'
        