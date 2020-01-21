import cv2
import time
import numpy as np

def create_boxes(layer_outputs, min_confidence, image_width, image_height):
	boxes = []
	confidences = []
	class_ids = []

	# loop over each of the layer outputs
	for output in layer_outputs:
		# loop over each of the detections
		for detection in output:
			# extract the class ID and confidence (i.e., probability) of
			# the current object detection
			scores = detection[5:]
			class_id = np.argmax(scores)
			confidence = scores[class_id]
	
			# filter out weak predictions by ensuring the detected
			# probability is greater than the minimum probability
			if confidence > min_confidence:
				# scale the bounding box coordinates back relative to the
				# size of the image, keeping in mind that YOLO actually
				# returns the center (x, y)-coordinates of the bounding
				# box followed by the boxes' width and height
				box = detection[0:4] * np.array([image_width, image_height, image_width, image_height])

				(center_x, center_y, width, height) = box.astype("int")
	
				# use the center (x, y)-coordinates to derive the top and
				# and left corner of the bounding box
				x = int(center_x - (width / 2))
				y = int(center_y - (height / 2))
	
				# update our list of bounding box coordinates, confidences,
				# and class IDs
				boxes.append([x, y, int(width), int(height)])
				confidences.append(float(confidence))
				class_ids.append(class_id)

	return (boxes, confidences, class_ids)

def yolo_image(darknet_config_path, yolo_weights_path, image_path, min_confidence, threshold):
	print("[INFO] Loading YOLO from disk")
	net = cv2.dnn.readNetFromDarknet(darknet_config_path, yolo_weights_path)

	print("[INFO] Loading image {} from disk".format(image_path))
	image = cv2.imread(image_path)
	(height, width) = image.shape[:2]

	layer_names = net.getLayerNames()
	layer_names = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

	blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)

	net.setInput(blob)
	start = time.time()
	layer_outputs = net.forward(layer_names)
	end = time.time()

	print("[INFO] Yolo took {:.6f} seconds".format(end - start))

	(boxes, confidences, class_ids) = create_boxes(layer_outputs, min_confidence, width, height)

	idxs = cv2.dnn.NMSBoxes(boxes, confidences, min_confidence,	threshold)
	if len(idxs) <= 0:
		return ([], [], [])
	
	idxs = idxs.flatten()

	boxes = [boxes[i] for i in idxs]
	confidences = [confidences[i] for i in idxs]
	class_ids = [class_ids[i] for i in idxs]

	return (boxes, confidences, class_ids)

def draw_boxes_on_image(image, boxes, box_labels, box_colors, confidences):
	for i in range(len(boxes)):
		# extract the bounding box coordinates
		(x, y) = (boxes[i][0], boxes[i][1])
		(w, h) = (boxes[i][2], boxes[i][3])

		# draw a bounding box rectangle and label on the image
		color = box_colors[i]
		cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
		text = "{}: {:.4f}".format(box_labels[i], confidences[i])
		cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
