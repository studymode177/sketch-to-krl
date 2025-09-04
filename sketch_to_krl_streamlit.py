import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="Sketch-to-KRL Code Generator",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("Sketch-to-KRL Code Generator")
st.markdown("""
This web application converts robot path sketches into KUKA Robot Language (KRL) code.
Upload a sketch or draw a path directly in the browser, then generate appropriate KRL programs.
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose the app mode", 
                                ["Upload Sketch", "Draw Sketch", "Generate KRL"])

# Utility functions
def process_image(image):
    """Process image to extract paths"""
    # Convert PIL image to OpenCV format
    opencv_image = np.array(image)
    opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to get binary image
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw contours on a black background
    contour_img = np.zeros_like(opencv_image)
    cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)
    
    return contour_img, contours

def extract_paths(contours):
    """Extract path information from contours"""
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

def paths_to_coordinates(paths, canvas_size=(400, 300)):
    """Convert path points to KRL coordinates"""
    krl_coordinates = []
    
    for path in paths:
        coords = []
        for point in path['points']:
            # Convert canvas coordinates to KRL coordinates with realistic robot workspace values
            # Assuming the robot workspace is 1000mm x 1000mm x 1000mm
            x = (point['x'] / canvas_size[0]) * 800 + 100  # Scale to 100-900mm range
            y = (point['y'] / canvas_size[1]) * 800 + 100  # Scale to 100-900mm range
            z = 300  # Default Z height for a consistent plane
            
            coords.append({
                'x': round(x, 2),
                'y': round(y, 2),
                'z': round(z, 2)
            })
        
        krl_coordinates.append(coords)
    
    return krl_coordinates

def generate_krl_code(start_position, motion_types, interpretation, clarifications, paths):
    """Generate KRL code based on user inputs and detected paths"""
    # Basic KRL program structure
    krl_code = "DEF sketch_program()\n"
    krl_code += "  INI\n"
    krl_code += "  \n"
    
    # Add global declarations
    krl_code += "  DECL E6POS home_position = {X 0, Y 0, Z 0, A 0, B 0, C 0, S 6, T 27}\n"
    krl_code += "  \n"
    
    # Add start position
    if start_position == "HOME":
        krl_code += "  ; Move to home position\n"
        krl_code += "  PTP home_position\n"
        krl_code += "  \n"
    
    # Convert paths to coordinates if needed
    if interpretation == "coordinates":
        coordinates = paths_to_coordinates(paths)
    else:
        coordinates = []
    
    # Add motion commands based on detected paths
    if paths:
        krl_code += "  ; Process detected paths from sketch\n"
        for i, path in enumerate(paths):
            if i < len(motion_types):
                motion_type = motion_types[i]
            else:
                motion_type = "PTP"  # Default motion type
            
            krl_code += f"  ; Path {i+1} motion\n"
            if motion_type == "PTP":
                if interpretation == "coordinates" and i < len(coordinates):
                    coord = coordinates[i][0] if coordinates[i] else {'x': 100, 'y': 200, 'z': 300}
                    krl_code += f"  PTP {{X {coord['x']}, Y {coord['y']}, Z {coord['z']}, A 0, B 0, C 0, S 6, T 27}}\n"
                else:
                    krl_code += f"  PTP {{X 100, Y 200, Z 300, A 0, B 0, C 0, S 6, T 27}} ; Default coordinates\n"
            elif motion_type == "LIN":
                if interpretation == "coordinates" and i < len(coordinates):
                    coord = coordinates[i][0] if coordinates[i] else {'x': 100, 'y': 200, 'z': 300}
                    krl_code += f"  LIN {{X {coord['x']}, Y {coord['y']}, Z {coord['z']}, A 0, B 0, C 0, S 6, T 27}} C_VEL\n"
                else:
                    krl_code += f"  LIN {{X 100, Y 200, Z 300, A 0, B 0, C 0, S 6, T 27}} C_VEL ; Default coordinates\n"
            elif motion_type == "CIRC":
                if interpretation == "coordinates" and i < len(coordinates) and len(coordinates[i]) >= 2:
                    coord1 = coordinates[i][0]
                    coord2 = coordinates[i][1]
                    krl_code += f"  CIRC {{X {coord1['x']}, Y {coord1['y']}, Z {coord1['z']}, A 0, B 0, C 0, S 6, T 27}}, {{X {coord2['x']}, Y {coord2['y']}, Z {coord2['z']}, A 0, B 0, C 0, S 6, T 27}} C_VEL\n"
                else:
                    krl_code += f"  CIRC {{X 150, Y 250, Z 350, A 0, B 0, C 0, S 6, T 27}}, {{X 200, Y 300, Z 400, A 0, B 0, C 0, S 6, T 27}} C_VEL ; Default coordinates\n"
            elif motion_type == "SPLINE":
                krl_code += f"  SPLINE\n"
                if interpretation == "coordinates" and i < len(coordinates):
                    for j, coord in enumerate(coordinates[i][:5]):  # Limit to first 5 points
                        krl_code += f"    SPL {{X {coord['x']}, Y {coord['y']}, Z {coord['z']}, A 0, B 0, C 0, S 6, T 27}}\n"
                else:
                    # Default spline points
                    krl_code += f"    SPL {{X 100, Y 200, Z 300, A 0, B 0, C 0, S 6, T 27}}\n"
                    krl_code += f"    SPL {{X 150, Y 250, Z 350, A 0, B 0, C 0, S 6, T 27}}\n"
                    krl_code += f"    SPL {{X 200, Y 300, Z 400, A 0, B 0, C 0, S 6, T 27}}\n"
                    krl_code += f"    SPL {{X 250, Y 350, Z 450, A 0, B 0, C 0, S 6, T 27}}\n"
                    krl_code += f"    SPL {{X 300, Y 400, Z 500, A 0, B 0, C 0, S 6, T 27}}\n"
                krl_code += f"  ENDSPLINE\n"
            krl_code += "  \n"
    else:
        # If no paths were detected, generate sample code
        krl_code += "  ; No paths detected in sketch, generating sample motions\n"
        for i, motion_type in enumerate(motion_types):
            if motion_type == "PTP":
                krl_code += f"  PTP {{X {100*(i+1)}, Y {200*(i+1)}, Z {300*(i+1)}, A 0, B 0, C 0, S 6, T 27}} ; Sample point {i+1}\n"
            elif motion_type == "LIN":
                krl_code += f"  LIN {{X {100*(i+1)}, Y {200*(i+1)}, Z {300*(i+1)}, A 0, B 0, C 0, S 6, T 27}} C_VEL ; Sample point {i+1}\n"
            elif motion_type == "CIRC":
                krl_code += f"  CIRC {{X {150*(i+1)}, Y {250*(i+1)}, Z {350*(i+1)}, A 0, B 0, C 0, S 6, T 27}}, {{X {200*(i+1)}, Y {300*(i+1)}, Z {400*(i+1)}, A 0, B 0, C 0, S 6, T 27}} C_VEL ; Sample points {i+1}\n"
            elif motion_type == "SPLINE":
                krl_code += f"  SPLINE\n"
                krl_code += f"    SPL {{X {100*(i+1)}, Y {200*(i+1)}, Z {300*(i+1)}, A 0, B 0, C 0, S 6, T 27}} ; Sample point {i+1}a\n"
                krl_code += f"    SPL {{X {150*(i+1)}, Y {250*(i+1)}, Z {350*(i+1)}, A 0, B 0, C 0, S 6, T 27}} ; Sample point {i+1}b\n"
                krl_code += f"    SPL {{X {200*(i+1)}, Y {300*(i+1)}, Z {400*(i+1)}, A 0, B 0, C 0, S 6, T 27}} ; Sample point {i+1}c\n"
                krl_code += f"  ENDSPLINE\n"
            krl_code += "  \n"
    
    # Add program end
    if start_position == "HOME":
        krl_code += "  ; Return to home position\n"
        krl_code += "  PTP home_position\n"
    krl_code += "END\n"
    
    return krl_code

# Main app logic
if app_mode == "Upload Sketch":
    st.header("Upload Sketch")
    st.markdown("Upload a PNG or JPG image of your robot path sketch:")
    
    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        # Process the uploaded image
        image = Image.open(uploaded_file)
        processed_image, contours = process_image(image)
        paths = extract_paths(contours)
        
        # Store paths in session state
        st.session_state.paths = paths
        
        # Display images
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Sketch")
            st.image(image, use_column_width=True)
        with col2:
            st.subheader("Processed Sketch")
            st.image(processed_image, channels="BGR", use_column_width=True)
        
        st.success(f"Detected {len(paths)} path(s) in your sketch!")
        if st.button("Generate KRL Code"):
            st.session_state.app_mode = "Generate KRL"
            st.experimental_rerun()

elif app_mode == "Draw Sketch":
    st.header("Draw Sketch")
    st.markdown("Draw your robot path directly in the browser:")
    
    # Drawing canvas using Streamlit components
    st.markdown("""
    <style>
    .canvas-container {
        border: 1px solid #ccc;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    </style>
    
    <div class="canvas-container">
        <canvas id="drawingCanvas" width="400" height="300"></canvas>
    </div>
    
    <button id="clearCanvas">Clear Canvas</button>
    
    <script>
    // Canvas drawing functionality
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    const clearBtn = document.getElementById('clearCanvas');
    
    // Set up canvas
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    
    // Drawing variables
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    
    function startDrawing(e) {
        isDrawing = true;
        [lastX, lastY] = [e.offsetX, e.offsetY];
    }
    
    function draw(e) {
        if (!isDrawing) return;
        
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
        
        [lastX, lastY] = [e.offsetX, e.offsetY];
    }
    
    function stopDrawing() {
        isDrawing = false;
    }
    
    // Add event listeners
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // Clear canvas
    clearBtn.addEventListener('click', function() {
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    });
    
    // Save canvas data to Streamlit
    function saveCanvas() {
        const dataURL = canvas.toDataURL('image/png');
        // In a real implementation, we would send this to Streamlit
    }
    </script>
    """, unsafe_allow_html=True)
    
    st.info("Note: The drawing functionality is currently limited in this Streamlit version. For best results, please upload an image of your sketch.")

elif app_mode == "Generate KRL":
    st.header("Generate KRL Code")
    
    # Get paths from session state or use empty list
    paths = st.session_state.get('paths', [])
    
    st.markdown("Answer the following questions to generate your KRL program:")
    
    # Start position selection
    start_position = st.radio("Start Position:", 
                              ["HOME (Standard robot home position)", 
                               "Anywhere (Current robot position)"])
    start_position = start_position.split(" ")[0]  # Extract "HOME" or "Anywhere"
    
    # Motion types for each path
    motion_types = []
    if paths:
        st.markdown(f"Based on your sketch, we detected {len(paths)} path(s). "
                    "Please select the appropriate motion type for each path:")
        
        for i in range(len(paths)):
            motion_type = st.radio(f"Path {i+1} Motion Type:", 
                                   ["PTP (Point-to-Point)", 
                                    "LIN (Linear)", 
                                    "CIRC (Circular)", 
                                    "SPLINE (Smooth path)"], 
                                   key=f"path_{i}")
            motion_type = motion_type.split(" ")[0]  # Extract motion type
            motion_types.append(motion_type)
    else:
        st.markdown("No paths detected in sketch. Please select a motion type for sample generation:")
        motion_type = st.radio("Motion Type:", 
                               ["PTP (Point-to-Point)", 
                                "LIN (Linear)", 
                                "CIRC (Circular)", 
                                "SPLINE (Smooth path)"])
        motion_type = motion_type.split(" ")[0]  # Extract motion type
        motion_types.append(motion_type)
    
    # Interpretation method
    interpretation = st.radio("Interpretation Method:", 
                             ["Direct sketch interpretation (use path shapes directly)", 
                              "With coordinates (convert sketch to specific coordinates)"])
    interpretation = "coordinates" if "With coordinates" in interpretation else "direct"
    
    # Clarifications
    clarifications = st.radio("Clarifications:", 
                             ["Yes (Ask for additional clarifications)", 
                              "No (Use default parameters)"])
    clarifications = "yes" if "Yes" in clarifications else "no"
    
    # Generate KRL code
    if st.button("Generate KRL Code"):
        krl_code = generate_krl_code(start_position, motion_types, interpretation, clarifications, paths)
        
        st.subheader("Generated KRL Code")
        st.code(krl_code, language="python")
        
        # Provide download option
        st.download_button(
            label="Download KRL Code",
            data=krl_code,
            file_name="sketch_program.src",
            mime="text/plain"
        )
        
        st.success("KRL code generated successfully!")