import cv2
import numpy as np
import os

class SketchProcessor:
    def __init__(self):
        pass
    
    def process_sketch(self, filepath):
        """
        Process a sketch image to extract paths and generate intermediate representation
        """
        # Read the image
        img = cv2.imread(filepath)
        
        if img is None:
            raise ValueError("Could not read image file")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw contours on a black background
        contour_img = np.zeros_like(img)
        cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)
        
        # Save processed image
        processed_filename = "processed_" + os.path.basename(filepath)
        processed_filepath = os.path.join('uploads', processed_filename)
        cv2.imwrite(processed_filepath, contour_img)
        
        # Extract path information
        paths = self.extract_paths(contours)
        
        return processed_filename, paths
    
    def extract_paths(self, contours):
        """
        Extract path information from contours
        """
        paths = []
        
        for i, contour in enumerate(contours):
            # Simplify contour using Ramer-Douglas-Peucker algorithm
            epsilon = 0.02 * cv2.arcLength(contour, True)
            simplified = cv2.approxPolyDP(contour, epsilon, True)
            
            # Extract points
            points = []
            for point in simplified:
                points.append({
                    'x': int(point[0][0]),
                    'y': int(point[0][1])
                })
            
            paths.append({
                'id': i,
                'points': points,
                'length': len(points)
            })
        
        return paths
    
    def paths_to_coordinates(self, paths, canvas_size=(400, 300)):
        """
        Convert path points to KRL coordinates
        """
        krl_coordinates = []
        
        for path in paths:
            coords = []
            for point in path['points']:
                # Convert canvas coordinates to KRL coordinates
                # This is a simplified conversion - in a real application, 
                # you would need to calibrate the coordinate system
                x = (point['x'] / canvas_size[0]) * 1000  # Scale to mm
                y = (point['y'] / canvas_size[1]) * 1000  # Scale to mm
                z = 0  # Assume all points are on the same plane
                
                coords.append({
                    'x': round(x, 2),
                    'y': round(y, 2),
                    'z': round(z, 2)
                })
            
            krl_coordinates.append(coords)
        
        return krl_coordinates