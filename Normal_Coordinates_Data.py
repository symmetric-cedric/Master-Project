import os
import re
import csv

def extract_value_from_section(log_file, section_header, mode, pattern):
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
                    value = float(match.group(1).replace('D', 'E'))
                    break
    except FileNotFoundError:
        print(f"Log file not found: {log_file}")
    except Exception as e:
        print(f"Error in {log_file}: {e}")
    return value

def compute_asymmetry(val_pos, val_neg):
    denominator = abs(val_pos) + abs(val_neg)
    if denominator == 0:
        return 0.0
    return (abs(val_pos) - abs(val_neg)) / denominator

def process_shift_directory(mode, base_dir):
    shift_dir = os.path.join(base_dir, f"Shift_{mode}")
    if not os.path.isdir(shift_dir):
        print(f"Directory not found: {shift_dir}")
        return []

    data = {}
    for fname in os.listdir(shift_dir):
        if not fname.endswith(".log"):
            continue

        match = re.match(rf"Benzene_Shift_{mode}_(-?\d+\.\d+)\.log", fname)
        if not match:
            continue

        mag = float(match.group(1))
        log_path = os.path.join(shift_dir, fname)
        hr = extract_value_from_section(log_path, "Huang-Rhys Factors", mode, r"Mode num\.\s+{}\s+- Factor:\s+([0-9.D+-]+)")
        shift = extract_value_from_section(log_path, "Shift Vector", mode, r"\s+{}\s+([0-9.D+-]+)")
        if hr is not None and shift is not None:
            data[mag] = (hr, shift)

    results = []
    checked = set()
    for mag in sorted(data.keys()):
        if mag < 0 or mag in checked:
            continue

        pos_mag = mag
        neg_mag = -mag

        if pos_mag in data and neg_mag in data:
            hr_pos, shift_pos = data[pos_mag]
            hr_neg, shift_neg = data[neg_mag]

            hr_asym = compute_asymmetry(hr_pos, hr_neg)
            shift_asym = compute_asymmetry(shift_pos, shift_neg)

            symmetry = "Symmetric" if (hr_asym == 0 and shift_asym == 0) else "Asymmetric"
            results.append((abs(pos_mag), hr_asym, shift_asym, symmetry))

            checked.add(pos_mag)
            checked.add(neg_mag)

    return sorted(results, key=lambda x: x[0])

def save_to_csv(results, output_file):
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Magnitude", "HR Asymmetry", "Shift Asymmetry", "Symmetry"])
        writer.writerows(results)
    print(f"Saved to {output_file}")

def main():
    mode = int(input("Enter mode number (X): "))
    base_dir = os.getcwd()
    output_file = f"Shift_{mode}_asymmetry_results.csv"
    results = process_shift_directory(mode, base_dir)
    save_to_csv(results, output_file)

if __name__ == "__main__":
    main()
