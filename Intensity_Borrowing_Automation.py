import os
import shutil
import subprocess
import numpy as np

def extract_mode(data: list, mode: int):
    """
    Extracts the atomic displacement vectors for the given mode.
    'mode' is assumed to be 1 for the first set, 2 for the second, or 3 for the third.
    """
    # Find the starting line of the displacement section.
    start_index = 0
    for i, line in enumerate(data):
        if line.strip().startswith("Atom  AN"):
            start_index = i + 1
            break

    displacements = []
    for line in data[start_index:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        # Each mode has 3 columns; first mode starts at index 2.
        base_index = 2 + (mode - 1) * 3
        coords = parts[base_index:base_index + 3]
        displacements.append([float(c) for c in coords])
    return np.array(displacements)

def extract_coordinates(data: list):
    """
    Extracts the atomic coordinates from a list of strings.
    Expects each line to look like: "C    0.000000   1.417367  -0.000000"
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
    Returns new atomic coordinates displaced by magnitude * frequency displacement.
    """
    return atom_coords + magnitude * freq_displacements

def format_output(displaced_coords: np.ndarray, atomic_data: list):
    """
    Formats displaced coordinates to match the original coordinate line format.
    """
    formatted_output = []
    for line, coords in zip(atomic_data, displaced_coords):
        parts = line.split()
        formatted_line = f"{parts[0]:<2}  {coords[0]:>10.6f}  {coords[1]:>10.6f}  {coords[2]:>10.6f}"
        formatted_output.append(formatted_line)
    return formatted_output

def update_sh_files(directory: str, new_dirname: str):
    """
    In every .sh file in 'directory', replace all occurrences of "Unshifted" with new_dirname.
    """
    for fname in os.listdir(directory):
        if fname.endswith(".sh"):
            fpath = os.path.join(directory, fname)
            with open(fpath, 'r') as f:
                content = f.read()
            new_content = content.replace("Unshifted", new_dirname)
            with open(fpath, 'w') as f:
                f.write(new_content)

def update_com_file(com_filepath: str, new_coords_lines: list):
    """
    Updates the coordinate section in a Gaussian input file.
    It locates the charge/multiplicity line (e.g., "0 1") and replaces the following block 
    (the coordinate lines) with new_coords_lines.
    """
    with open(com_filepath, 'r') as f:
        lines = f.readlines()

    # Find the charge/multiplicity line (assumed to be a line with exactly two numbers)
    charge_line_index = None
    for idx, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) == 2:
            try:
                float(parts[0])
                float(parts[1])
                charge_line_index = idx
                break
            except ValueError:
                continue
    if charge_line_index is None:
        raise ValueError("Could not find charge/multiplicity line in .com file.")

    new_file_lines = lines[:charge_line_index+1]

    # Skip over the old coordinate lines (assumed to continue until a blank line)
    coord_end_index = charge_line_index+1
    while coord_end_index < len(lines) and lines[coord_end_index].strip():
        coord_end_index += 1

    new_file_lines.extend([line + "\n" for line in new_coords_lines])
    
    if coord_end_index < len(lines) and lines[coord_end_index].strip() == "":
        new_file_lines.append("\n")
        new_file_lines.extend(lines[coord_end_index+1:])
    else:
        new_file_lines.extend(lines[coord_end_index:])

    with open(com_filepath, 'w') as f:
        f.writelines(new_file_lines)

def main():
    # --------------------------
    # Read frequency data.
    # --------------------------
    print("Enter the frequency data (type 'END' on a new line to finish):")
    frequency_data = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        frequency_data.append(line.rstrip())

    # Attempt to use the first non-empty line as header tokens.
    header_tokens = []
    for line in frequency_data:
        if line.strip():
            tokens = line.split()
            # Here we expect tokens like "10", "11", "12" etc.
            header_tokens = tokens
            break

    # --------------------------
    # Mode selection: allow using modulo arithmetic.
    # --------------------------
    while True:
        try:
            user_mode_input = int(input("Enter the mode to extract (e.g. 11): "))
            if header_tokens and str(user_mode_input) in header_tokens:
                # Use the token position from the header.
                mode_index = header_tokens.index(str(user_mode_input)) + 1
                print(f"Mode {user_mode_input} found in header. Using displacement column {mode_index}.")
            else:
                # Otherwise, use modulo arithmetic.
                mode_index = user_mode_input % 3
                if mode_index == 0:
                    mode_index = 3
                print(f"Using mode index {mode_index} from user input {user_mode_input} with modulo arithmetic.")
            break
        except ValueError:
            print("Invalid input. Please enter an integer value.")

    # --------------------------
    # Read atomic coordinates.
    # --------------------------
    print("Enter the formatted atomic coordinates (type 'END' on a new line to finish):")
    atomic_data = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        atomic_data.append(line.rstrip())

    # --------------------------
    # Read displacement magnitudes.
    # --------------------------
    print("Enter the magnitude values for displacement (type 'END' on a new line to finish):")
    magnitudes = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        try:
            mag = float(line)
            magnitudes.append(mag)
        except ValueError:
            print("Invalid input. Please enter a numerical value.")

    # --------------------------
    # Compute displacements.
    # --------------------------
    freq_displacements = extract_mode(frequency_data, mode_index)
    atom_coords = extract_coordinates(atomic_data)

    for mag in magnitudes:
        displaced_coords = displace_atoms(atom_coords, freq_displacements, mag)
        formatted_output = format_output(displaced_coords, atomic_data)
        
        # Create new directory name, e.g. "Unshifted_Shift_11_0.05"
        new_dirname = f"Unshifted_Shift_{user_mode_input}_{mag:.8f}".rstrip("0").rstrip(".")
        print(f"\nProcessing for magnitude {mag} in directory {new_dirname}")

        src_dir = "Unshifted"
        if not os.path.isdir(src_dir):
            print(f"Source directory '{src_dir}' does not exist. Exiting.")
            return
        if os.path.exists(new_dirname):
            print(f"Directory {new_dirname} already exists. It will be overwritten.")
            shutil.rmtree(new_dirname)
        shutil.copytree(src_dir, new_dirname)
        
        update_sh_files(new_dirname, new_dirname)
        
        com_filepath = os.path.join(new_dirname, "PW6B95D3_N_ES_Opt.com")
        if not os.path.isfile(com_filepath):
            print(f"{com_filepath} not found. Skipping coordinate update.")
        else:
            update_com_file(com_filepath, formatted_output)
        
        # Submit the job using the script filename relative to new_dirname.
        sh_filename = "PW6B95D3_N_ES_Opt.sh"
        sh_filepath = os.path.join(new_dirname, sh_filename)
        if os.path.isfile(sh_filepath):
            try:
                subprocess.run(["qsub", sh_filename], check=True, cwd=new_dirname)
                print(f"Job submitted for {new_dirname}")
            except subprocess.CalledProcessError as e:
                print(f"Job submission failed for {new_dirname}: {e}")
        else:
            print(f"{sh_filepath} not found. Skipping job submission.")

if __name__ == "__main__":
    main()
