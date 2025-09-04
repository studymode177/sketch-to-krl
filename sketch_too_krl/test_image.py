import cv2
import numpy as np

# Create a simple test image with paths
img = np.ones((300, 400, 3), dtype=np.uint8) * 255  # White background

# Draw some paths
# Path 1: Straight line
cv2.line(img, (50, 50), (200, 50), (0, 0, 0), 2)

# Path 2: Diagonal line
cv2.line(img, (50, 100), (200, 200), (0, 0, 0), 2)

# Path 3: Circle
cv2.circle(img, (300, 150), 30, (0, 0, 0), 2)

# Path 4: Rectangle
cv2.rectangle(img, (250, 200), (350, 250), (0, 0, 0), 2)

# Save the test image
cv2.imwrite('test_sketch.png', img)
print("Test sketch created successfully!")