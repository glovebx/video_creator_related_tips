# Importing Libraries
import numpy as np
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

from PIL import Image, ImageDraw, ImageFont


# 检测手臂的在这里
# https://github.com/nicknochnack/MediaPipePoseEstimation/blob/main/Media%20Pipe%20Pose%20Tutorial.ipynb

# Used to convert protobuf message to a dictionary.
from google.protobuf.json_format import MessageToDict

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def get_bbox_coordinates(hand_landmark, image_shape):
    """ 
    Get bounding box coordinates for a hand landmark.
    Args:
        handLadmarks: A HandLandmark object.
        image_shape: A tuple of the form (height, width).
    Returns:
        A tuple of the form (xmin, ymin, xmax, ymax).
    """
    all_x, all_y = [], [] # store all x and y points in list
    for hnd in mpHands.HandLandmark:
        all_x.append(int(hand_landmark.landmark[hnd].x * image_shape[1])) # multiply x by image width
        all_y.append(int(hand_landmark.landmark[hnd].y * image_shape[0])) # multiply y by image height

    return min(all_x), min(all_y), max(all_x), max(all_y) # return as (xmin, ymin, xmax, ymax)


# Initializing the Model
mpHands = mp.solutions.hands
hands = mpHands.Hands(
	static_image_mode=True,
	model_complexity=1,
	min_detection_confidence=0.75,
	min_tracking_confidence=0.75,
	max_num_hands=2)


# Read video frame by frame
img = cv2.imread('test2.jpg')

# Flip the image(frame)
img = cv2.flip(img, 1)

# Convert BGR image to RGB image
imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Process the RGB image
results = hands.process(imgRGB)

image_height, image_width, c = img.shape # get image shape

# If hands are present in image(frame)
if results.multi_hand_landmarks:

	# Both Hands are present in image(frame)
	if len(results.multi_handedness) == 2:
			# Display 'Both Hands' on the image
		cv2.putText(img, 'Both Hands', (250, 50),
					cv2.FONT_HERSHEY_COMPLEX,
					0.9, (0, 255, 0), 2)

	# If any hand present
	else:
		for i in results.multi_handedness:
			
			# Return whether it is Right or Left Hand

			mtd = MessageToDict(i)
			print(mtd)
			classification = mtd['classification']
			label = classification[0]['label']

			print(label)

			if label == 'Left':
				
				# Display 'Left Hand' on
				# left side of window
				cv2.putText(img, label+' Hand',
							(20, 50),
							cv2.FONT_HERSHEY_COMPLEX,
							0.9, (0, 255, 0), 2)

			if label == 'Right':
				
				# Display 'Left Hand'
				# on left side of window
				cv2.putText(img, label+' Hand', (460, 50),
							cv2.FONT_HERSHEY_COMPLEX,
							0.9, (0, 255, 0), 2)

	# iterate on all detected hand landmarks
	for hand_landmark in results.multi_hand_landmarks:
		# print(hand_landmark)
	    #   # # we can get points using mp_hands
		# print(f'Ring finger tip coordinates: (',
		# 	f'{hand_landmark.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x * image_width}, '
		# 	f'{hand_landmark.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y * image_height})'
		# )
		mp_drawing.draw_landmarks(img, hand_landmark, mp_hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())	      

		rect = get_bbox_coordinates(hand_landmark, (image_height, image_width))
		print(rect)
		draw_rects(img, [rect], (255, 0, 0))

# Display Video and when 'q'
# is entered, destroy the window
cv2.imshow('Image', img)

cv2.waitKey(0) 
   
cv2.destroyAllWindows()
# if cv2.waitKey(1) & 0xff == ord('q'):
# 	break
