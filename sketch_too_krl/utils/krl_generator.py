class KRLGenerator:
    def __init__(self):
        pass
    
    def generate_program(self, start_position, motion_types, interpretation, clarifications, paths):
        """
        Generate a complete KRL program based on user inputs and detected paths
        """
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
            coordinates = self.paths_to_coordinates(paths)
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
    
    def paths_to_coordinates(self, paths, canvas_size=(400, 300)):
        """
        Convert path points to KRL coordinates with more realistic values
        """
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