import numpy as np

def get_coordinates():
    """
    Get user input for coordinates and convert them into a numerical array.
    """
    print("Enter the Coordinates (type 'END' on a new line to finish):")
    coordinates = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        parts = line.split()
        # Extract only the x, y, z coordinates (last three elements)
        coordinates.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return np.array(coordinates)

def calculate_plane_normal(coords):
    """
    Calculate the normal vector of a plane defined by 3 points.
    """
    # Use the first three points to define the plane
    p1, p2, p3 = coords[:3]
    v1 = p2 - p1
    v2 = p3 - p1
    # Cross product gives the normal vector to the plane
    normal = np.cross(v1, v2)
    # Normalize the vector
    normal /= np.linalg.norm(normal)
    return normal

def adjust_angle(angle_degrees):
    """
    Adjust the angle such that if it is greater than 90°, return 180 - angle.
    """
    if angle_degrees > 90:
        return 180 - angle_degrees
    else:
        pass
    return angle_degrees

def calculate_angle_between_planes(coords):
    """
    Calculate the angle between two benzene rings given their atomic coordinates.
    """
    # Split into two rings
    ring1_coords = coords[:6]  # First 6 lines for ring 1
    ring2_coords = coords[6:]  # Last 6 lines for ring 2
    
    # Calculate the plane normals for each ring
    normal1 = calculate_plane_normal(ring1_coords)
    normal2 = calculate_plane_normal(ring2_coords)
    
    # Calculate the angle between the two normals
    dot_product = np.dot(normal1, normal2)
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))  # Clip to handle numerical precision issues
    angle_degrees = np.degrees(angle)  # Convert to degrees
    return adjust_angle(angle_degrees)

# Input coordinates
coordinates = get_coordinates()

# Compute the angle between the two benzene rings
angle = calculate_angle_between_planes(coordinates)
print(f"The angle between the two benzene rings is: {angle:.2f} degrees")
