import cv2
import numpy as np
import os

# Create the uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)

# Create a simple test image with paths
img = np.ones((300, 400, 3), dtype=np.uint8) * 255  # White background

# Draw some paths
# Path 1: Straight line (PTP motion)
cv2.line(img, (50, 50), (200, 50), (0, 0, 0), 2)

# Path 2: Diagonal line (LIN motion)
cv2.line(img, (50, 100), (200, 200), (0, 0, 0), 2)

# Path 3: Circle (CIRC motion)
cv2.circle(img, (300, 150), 30, (0, 0, 0), 2)

# Path 4: Rectangle (SPLINE motion)
cv2.rectangle(img, (250, 200), (350, 250), (0, 0, 0), 2)

# Save the test image in the uploads directory
cv2.imwrite('uploads/sample_sketch.png', img)
print("Sample sketch 'sample_sketch.png' created successfully in uploads directory!")