import numpy as np
import cv2

# Read input image
img = cv2.imread('test.jpg')

# Convert from BGR to HSV color space
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Get the saturation plane - all black/white/gray pixels are zero, and colored pixels are above zero.
s = hsv[:, :, 1]

# Apply threshold on s - use automatic threshold algorithm (use THRESH_OTSU).
ret, thresh = cv2.threshold(s, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

# Find contours in thresh (find only the outer contour - only the rectangle).
contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # [-2] indexing takes return value before last (due to OpenCV compatibility issues).

areas = [cv2.contourArea(c) for c in contours]
max_index = np.argmax(areas)
cnt = contours[max_index]
x, y, w, h = cv2.boundingRect(cnt)
crop_img = img[y-64:y+h+64, x-64:x+w+64]

cv2.imwrite('result.jpg', crop_img)

# # Mark rectangle with green line
# cv2.drawContours(img, contours, -1, (0, 255, 0), 2)

# # Assume there is only one contour, get the bounding rectangle of the contour.
# x, y, w, h = cv2.boundingRect(contours[0])

# # Invert polarity of the pixels inside the rectangle (on thresh image).
# thresh[y:y+h, x:x+w] = 255 - thresh[y:y+h, x:x+w]

# # Find contours in thresh (find the triangles).
# contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # [-2] indexing takes return value before last (due to OpenCV compatibility issues).

# # Iterate triangle contours
# for c in contours:
#     if cv2.contourArea(c) > 4:  #  Ignore very small contours
#         # Mark triangle with blue line
#         cv2.drawContours(img, [c], -1, (255, 0, 0), 2)

# Show result (for testing).
cv2.imshow('img', crop_img)
cv2.waitKey(0)
cv2.destroyAllWindows()