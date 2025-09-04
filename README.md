# Sketch-to-KRL Code Generator

This is a Streamlit web application that converts robot path sketches into KUKA Robot Language (KRL) code.

## Features

- Upload PNG or JPG sketches of robot paths
- Automatic path detection using OpenCV
- Interactive Q&A flow to customize KRL generation
- Support for multiple motion types: PTP, LIN, CIRC, SPLINE
- Coordinate conversion from sketch to robot workspace
- Download generated KRL code

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the Streamlit app:
   ```
   streamlit run sketch_to_krl_streamlit.py
   ```

## Usage

1. Upload a PNG or JPG image of your robot path sketch
2. The app will process the image and detect paths
3. Answer the questions about start position and motion types
4. View and download the generated KRL code

## Deploying to Streamlit Cloud

To deploy this app to Streamlit Community Cloud:

1. Create a GitHub repository with these files
2. Go to https://streamlit.io/cloud
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository
6. Set the main file path to `sketch_to_krl_streamlit.py`
7. Click "Deploy"