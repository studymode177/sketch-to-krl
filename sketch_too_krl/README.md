# Sketch-to-KRL Code Generator

This web application converts robot path sketches into KUKA Robot Language (KRL) code. Users can either upload an image of a sketch or draw a path directly in the browser.

## Features

- Upload PNG or JPG sketches of robot paths
- Draw paths directly in the browser using the canvas tool
- Automatic path detection using OpenCV
- Interactive Q&A flow to customize KRL generation
- Support for multiple motion types: PTP, LIN, CIRC, SPLINE
- Coordinate conversion from sketch to robot workspace

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Access the application at `http://localhost:5000`

## Usage

1. **Upload a sketch**:
   - Click on "Upload Sketch" tab
   - Select a PNG or JPG file containing your robot path sketch
   - The application will process the image and detect paths

2. **Draw a sketch**:
   - Click on "Draw Sketch" tab
   - Use your mouse to draw paths on the canvas
   - Save and process the drawing (coming soon)

3. **Generate KRL code**:
   - After processing a sketch, you'll be prompted to generate KRL code
   - Answer the questions about start position and motion types
   - Choose between direct sketch interpretation or coordinate-based generation
   - View and copy the generated KRL code

## KRL Motion Types

- **PTP (Point-to-Point)**: Moves each axis independently to reach the target position as quickly as possible
- **LIN (Linear)**: Moves the tool center point (TCP) in a straight line
- **CIRC (Circular)**: Moves the TCP along a circular path through three points
- **SPLINE**: Creates smooth, continuous paths through multiple points

## Technical Details

The application uses OpenCV for image processing to detect paths in sketches. It then converts these paths into appropriate KRL motion commands based on user preferences.

The coordinate conversion assumes a robot workspace of 1000mm x 1000mm x 1000mm and maps the sketch coordinates to this workspace.

## File Structure

```
sketch_to_krl/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── process.html
│   ├── generate.html
│   └── result.html
├── static/             # Static files (CSS, JS, images)
├── uploads/            # Uploaded images
└── utils/              # Utility modules
    ├── image_processor.py
    └── krl_generator.py
```