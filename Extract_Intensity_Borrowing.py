import os
import re
import csv

def extract_value_from_section(log_file, section_header, mode, pattern):
    """
    Extracts a numerical value from a specified section in a Gaussian log file.
    """
    value = None
    try:
        with open(log_file, 'r') as file:
            lines = file.readlines()
        
        inside_section = False
        for line in lines:
            if section_header in line:
                inside_section = True
                continue
            
            if inside_section:
                match = re.search(pattern.format(mode), line)
                if match:
                    value = float(match.group(1).replace('D', 'E'))  # Convert scientific notation
                    break
    except FileNotFoundError:
        print(f"Log file not found: {log_file}")
    except Exception as e:
        print(f"An error occurred while processing {log_file}: {e}")
    return value

def extract_transition_modes_and_dipstr(log_file,Y):
    """Extracts the dipole strength from a Gaussian log file."""
    dipole_strength = None
    try:
        with open(log_file, 'r') as file:
            lines = file.readlines()
        
        for i in range(len(lines) - 1):  # Iterate with index
            if f"|0> -> |{Y}^1>" in lines[i]:  # Directly search for transition
                dipstr_match = re.search(r"DipStr = ([0-9.E+-]+)", lines[i + 1])
                if dipstr_match:
                    dipole_strength = float(dipstr_match.group(1))
                    break
    except FileNotFoundError:
        print(f"Log file not found: {log_file}")
    except Exception as e:
        print(f"An error occurred while processing {log_file}: {e}")
    return dipole_strength

def process_directories(X, Y, base_dir):
    """Recursively find relevant subdirectories and extract data."""
    results = []
    
    for root, _, files in os.walk(base_dir):
        dir_name = os.path.basename(root)
        match = re.match(fr'{X}_Shift_{Y}_(-?\d+\.\d+)', dir_name)  # Allow negative values
        
        if match:
            magnitude_of_shift = float(match.group(1))
            abs_log = os.path.join(root, "PW6B95D3_N_FCHT_ABS.log")
            emi_log = os.path.join(root, "PW6B95D3_N_FCHT_EMI.log")
            
            
            dipstr_abs = extract_transition_modes_and_dipstr(abs_log,Y) if os.path.exists(abs_log) else None
            dipstr_emi = extract_transition_modes_and_dipstr(emi_log,Y) if os.path.exists(emi_log) else None
            
            huang_rhys = extract_value_from_section(abs_log, "Huang-Rhys Factors", Y, r"Mode num\.\s+{}\s+- Factor:\s+([0-9.D+-]+)") if os.path.exists(abs_log) else None
            shift_value = extract_value_from_section(abs_log, "Shift Vector", Y, r"\s+{}\s+([0-9.D+-]+)") if os.path.exists(abs_log) else None
            
            results.append((magnitude_of_shift, huang_rhys, shift_value, dipstr_abs, dipstr_emi))
    
    return sorted(results)  # Sort by magnitude of shift

def save_to_csv(results, output_file):
    """Saves extracted data to a CSV file."""
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Magnitude", "Huang-Rhys", "Shift", "ABS", "EMI"])
        writer.writerows(results)
    print(f"Data successfully saved to {output_file}")

def main():
    X = "Unshifted"
    Y = int(input("Enter Y (Mode number that is being shifted along): "))
    base_dir = os.getcwd()
    output_file = f"{X}_{Y}_dipole_strengths.csv"
    
    results = process_directories(X, Y, base_dir)
    save_to_csv(results, output_file)

if __name__ == "__main__":
    main()
