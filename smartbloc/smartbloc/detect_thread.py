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
    
    def run(self):  
        print("[DETECT THREAD] Running...")
        start_time = time.time()

        try:
            img = image_lib.get_camera_image()
            (h, w) = img.shape[0:2]

            image_lib.store_image(img, image_lib.CAMERA_IMAGE_PATH)

            (boxes, confidences, class_ids) = yolo.yolo_image(CONFIG_PATH, WEIGHTS_PATH,
                image_lib.CAMERA_IMAGE_PATH, CONFIDENCE, THRESHOLD)
            
            box_labels = [LABELS[i] for i in class_ids]
            box_colors = [COLORS[i].tolist() for i in class_ids]

            if self.is_on_top(boxes, confidences, box_labels):
                print("[DETECT THREAD] Top reached !")
                self.top_reached = True
            
            if self.is_on_bottom(h, boxes, confidences, box_labels):
                print("[DETECT THREAD] Bottom reached !")
                if self.top_reached:
                    print("[DETECT THREAD] Done !")
                    self.done = True

            # Draw boxes on image
            yolo.draw_boxes_on_image(img, boxes, box_labels, box_colors, confidences)
            
            # Draw margins on image
            cv2.rectangle(img, (0, 0), (w, settings.CAMERA_MARGIN_TOP), (255, 0, 0), 2)
            cv2.rectangle(img, (0, h - settings.CAMERA_MARGIN_BOTTOM), (w, h), (255, 0, 0), 2)


            image_lib.store_image(img, image_lib.YOLO_IMAGE_PATH)

            self.remaining_trials = 5
        except OSError as e:
            print("[DETECT THREAD] [ERROR] Camera not available: ", e)
            if self.remaining_trials <= 0:
                print("[DETECT THREAD] ABORTING THREAD AFTER 5 ATTEMPS")
                return
            
            self.remaining_trials -= 1
        

        end_time = time.time()
        loop_duration = end_time - start_time
        print("[DETECT THREAD] Loop duration: {:.6f}".format(loop_duration))

        if not self.running:
            return
        
        if loop_duration < DETECT_THREAD_PERIOD_MS:
            time.sleep(float(DETECT_THREAD_PERIOD_MS - loop_duration) / 1000.0)
        
        self.run()

    def is_on_top(self, boxes, confidences, labels):
        for i in range(len(boxes)):
            if labels[i] == 'person':
                (_, y) = (boxes[i][0], boxes[i][1])
                (_, h) = (boxes[i][2], boxes[i][3])

                print("[DETECT THREAD] Person found at {} with height of {}".format(y, h))
                if y <= settings.CAMERA_MARGIN_TOP:
                    return True

    def is_on_bottom(self, img_height, boxes, confidences, labels):
        for i in range(len(boxes)):
            if labels[i] == 'person':
                (_, y) = (boxes[i][0], boxes[i][1])
                (_, h) = (boxes[i][2], boxes[i][3])

                if y + h >= img_height - settings.CAMERA_MARGIN_BOTTOM:
                    return True

def create_new_thread():
    global current_detect_thread

    if current_detect_thread is not None:
        current_detect_thread.running = False
        current_detect_thread.join()
    
    current_detect_thread = DetectThread()
    current_detect_thread.start()
