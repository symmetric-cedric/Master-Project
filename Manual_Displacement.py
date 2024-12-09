import numpy as np

def extract_mode(data: list, mode: int):
    """
    Extracts the atomic displacement vectors for a specific mode from the input data.

    Args:
        data (list): Input data containing mode information as a list of strings.
        mode (int): The mode to extract (1, 2, or 3).

    Returns:
        np.ndarray: A NumPy array containing the displacement vectors for the selected mode.
    """
    if mode not in [1, 2, 3]:
        raise ValueError("Mode must be 1, 2, or 3")

    # Find the starting line of the coordinates section
    start_index = 0
    for i, line in enumerate(data):
        if line.strip().startswith("Atom  AN"):
            start_index = i + 1
            break

    # Extract the relevant displacement vectors
    displacements = []
    for line in data[start_index:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        base_index = 2 + (mode - 1) * 3
        coords = parts[base_index:base_index + 3]
        displacements.append([float(c) for c in coords])

    return np.array(displacements)


def extract_coordinates(data: list):
    """
    Extracts the atomic coordinates from a list of strings.

    Args:
        data (list): Input list where each element is a string containing atomic data.

    Returns:
        np.ndarray: A NumPy array containing the atomic coordinates as floats.
    """
    coordinates = []

    for line in data:
        parts = line.split()
        if len(parts) < 4:
            continue
        coords = [float(parts[1]), float(parts[2]), float(parts[3])]
        coordinates.append(coords)

    return np.array(coordinates)


def displace_atoms(atom_coords: np.ndarray, freq_displacements: np.ndarray, magnitude: float):
    """
    Displaces atomic coordinates based on frequency displacements and a magnitude.

    Args:
        atom_coords (np.ndarray): Original atomic coordinates.
        freq_displacements (np.ndarray): Frequency displacement vectors for each atom.
        magnitude (float): Magnitude of displacement.

    Returns:
        np.ndarray: Displaced atomic coordinates.
    """
    return atom_coords + magnitude * freq_displacements


def format_output(displaced_coords: np.ndarray, atomic_data: list):
    """
    Formats the displaced atomic coordinates into the original data format.

    Args:
        displaced_coords (np.ndarray): Displaced atomic coordinates.
        atomic_data (list): Original atomic data lines for reference.

    Returns:
        list: A list of formatted strings with displaced coordinates.
    """
    formatted_output = []
    for line, coords in zip(atomic_data, displaced_coords):
        parts = line.split()
        formatted_line = f"{parts[0]:<2}  {coords[0]:>10.6f}  {coords[1]:>10.6f}  {coords[2]:>10.6f}"
        formatted_output.append(formatted_line)
    return formatted_output


# Interactive input for frequency data
print("Enter the frequency data (type 'END' on a new line to finish):")
frequency_data = []
while True:
    line = input()
    if line.strip().upper() == "END":
        break
    frequency_data.append(line.strip())

# Interactive input for mode selection
while True:
    try:
        mode = int(input("Enter the mode to extract (1, 2, or 3): "))
        if mode in [1, 2, 3]:
            break
        else:
            print("Invalid input. Please enter 1, 2, or 3.")
    except ValueError:
        print("Invalid input. Please enter an integer value.")

# Interactive input for atomic data
print("Enter the formatted atomic coordinates (type 'END' on a new line to finish):")
atomic_data = []
while True:
    line = input()
    if line.strip().upper() == "END":
        break
    atomic_data.append(line.strip())

# Interactive input for magnitude
while True:
    try:
        magnitude = float(input("Enter the magnitude of displacement: "))
        break
    except ValueError:
        print("Invalid input. Please enter a numerical value.")

# Process data
freq_displacements = extract_mode(frequency_data, mode)
atom_coords = extract_coordinates(atomic_data)
displaced_coords = displace_atoms(atom_coords, freq_displacements, magnitude)
formatted_output = format_output(displaced_coords, atomic_data)

# Display displaced atomic coordinates
print("\nDisplaced Atomic Coordinates:")
for line in formatted_output:
    print(line)
