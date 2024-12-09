import os

def format_time_unit(number):
    """Formats a number to be at least two digits."""
    return f"{number:02}"

def get_coordinates(label):
    """Prompts the user to enter coordinates."""
    print(f"Enter the {label} Coordinates (type 'END' on a new line to finish):")
    coordinates = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        coordinates.append(line)
    return coordinates


def create_pbs_and_com_scripts():
    """Generates PBS and .com scripts with corrected GS_Ver structure."""
    # Collecting user inputs
    hours = format_time_unit(int(input("Enter Hours Needed (0-23): ")))
    minutes = format_time_unit(int(input("Enter Minutes Needed (0-59): ")))
    seconds = format_time_unit(int(input("Enter Seconds Needed (0-59): ")))
    time_limit = f"{hours}:{minutes}:{seconds}"
    cores = int(input("Enter Number of Cores: "))
    memory_gb = int(input("Enter Memory Needed (in GB): "))
    molecule_name = input("Enter Molecule Name: ").strip()
    calculation_state = input("Enter State (GS_Opt/ES_Opt/GS_Ver/ES_Ver/ABS/EMI): ").strip() 
    script_name = f"{molecule_name}_{calculation_state}"

    # Handle additional inputs for ABS and EMI states
    if calculation_state in ["ABS", "EMI"]:
        opt_energy = float(input("Enter the Optimized Energy: "))
        vertical_trans_energy = float(input("Enter the Vertical Transitioned Energy: "))
        delta_e = abs(opt_energy - vertical_trans_energy)
    else:
        delta_e = None  # Not needed for GS_Opt, ES_Opt, GS_Ver, or ES_Ver

    # Define the target directory path
    home_dir = os.path.expanduser("~")
    target_dir = os.path.join(home_dir, "Master_Project", "test", molecule_name)

    # Create the directory if it doesn't exist
    try:
        os.makedirs(target_dir, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {target_dir}: {e}")
        return

    # Define file paths
    sh_filename = os.path.join(target_dir, f"{script_name}.sh")
    com_filename = os.path.join(target_dir, f"{script_name}.com")

    # Get coordinates only for GS_Opt and ES_Opt
    if calculation_state in ["GS_Opt", "ES_Opt"]:
        coordinates = get_coordinates(calculation_state)

    # Write the PBS script to the .sh file
    try:
        with open(sh_filename, "w") as sh_file:
            sh_file.write("#!/bin/bash\n")
            sh_file.write(f"#PBS -l walltime={time_limit}\n")
            sh_file.write(f"#PBS -l select=1:ncpus={cores}:mem={memory_gb}gb\n")
            sh_file.write(f"#PBS -N {script_name}_Calculation\n\n")
            sh_file.write('module load "gaussian/g16-c01-avx2"\n')

            if calculation_state in ["ABS", "EMI", "ES_Ver"]: 
                sh_file.write(f"cp $HOME/Master_Project/test/{molecule_name}/{molecule_name}_GS_Opt.chk $TMPDIR\n")
            if calculation_state in ["ABS", "EMI", "GS_Ver"]: 
                sh_file.write(f"cp $HOME/Master_Project/test/{molecule_name}/{molecule_name}_ES_Opt.chk $TMPDIR\n") 

            sh_file.write(f"cp $HOME/Master_Project/test/{molecule_name}/{script_name}.com $TMPDIR\n")
            sh_file.write(f"g16 {script_name}.com\n")
            sh_file.write(f"cp $TMPDIR/*.log $HOME/Master_Project/test/{molecule_name}/\n")
            if calculation_state in ["GS_Opt", "ES_Opt"]:
                sh_file.write(f"cp $TMPDIR/{script_name}.chk $HOME/Master_Project/test/{molecule_name}/\n")
    except OSError as e:
        print(f"Error writing to file {sh_filename}: {e}")
        return

    # Write the Gaussian input script to the .com file
    try:
        with open(com_filename, "w") as com_file:
            if calculation_state == "GS_Opt":
                # Ground State Optimization Calculation
                com_file.write(f"%Mem={memory_gb}GB\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%chk={molecule_name}_GS_Opt_Part1.chk\n")
                com_file.write("#p opt pm6\n\n")
                com_file.write("Ground State Optimization Calculation Part 1\n\n")
                com_file.write("0 1\n")
                com_file.write("\n".join(coordinates) + "\n\n")
                com_file.write("--Link1--\n")
                com_file.write(f"%Mem={memory_gb}GB\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%oldchk={molecule_name}_GS_Opt_Part1.chk\n")
                com_file.write(f"%chk={molecule_name}_GS_Opt_Part2.chk\n\n")
                com_file.write("#p B3LYP/6-31G geom=check opt\n\n")
                com_file.write("Ground State Optimization Calculation Part 2\n\n")
                com_file.write("0 1\n\n")
                com_file.write("--Link1--\n")
                com_file.write(f"%Mem={memory_gb}GB\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%oldchk={molecule_name}_GS_Opt_Part2.chk\n")
                com_file.write(f"%chk={molecule_name}_GS_Opt.chk\n\n")
                com_file.write("#p B3LYP/def2TZVP geom=check opt freq=savenormalmodes\n\n")
                com_file.write("Ground state optimization and frequency calculation\n\n")
                com_file.write("0 1\n")
            elif calculation_state == "ES_Opt":
                # Excited State Optimization Calculation
                com_file.write(f"%Mem={memory_gb}GB\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%chk={molecule_name}_ES_Opt_Part1.chk\n")
                com_file.write("#p opt b3lyp/sto-3g TD=(nstates=2, Root=1)\n\n")
                com_file.write("Excited State Optimization Calculation Part 1\n\n")
                com_file.write("0 1\n")
                com_file.write("\n".join(coordinates) + "\n\n")
                com_file.write("--Link1--\n")
                com_file.write(f"%Mem={memory_gb}GB\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%oldchk={molecule_name}_ES_Opt_Part1.chk\n")
                com_file.write(f"%chk={molecule_name}_ES_Opt_Part2.chk\n\n")
                com_file.write("#p opt b3lyp/6-31G TD=(nstates=2, Root=1) geom=check\n\n")
                com_file.write("Excited State Optimization Calculation Part 2\n\n")
                com_file.write("0 1\n\n")
                com_file.write("--Link1--\n")
                com_file.write(f"%Mem={memory_gb}GB\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%oldchk={molecule_name}_ES_Opt_Part2.chk\n")
                com_file.write(f"%chk={molecule_name}_ES_Opt.chk\n\n")
                com_file.write("#p opt freq=savenormalmodes b3lyp/def2tzvp TD=(nstates=2, Root=1) geom=check\n\n")
                com_file.write("Excited state optimization and frequency calculation\n\n")
                com_file.write("0 1\n")
            elif calculation_state == "GS_Ver":
                # Ground State Verification Calculation (Corrected)
                com_file.write(f"%Mem={memory_gb}GB\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%oldchk={molecule_name}_ES_Opt.chk\n")
                com_file.write(f"%chk={molecule_name}_GS_Ver.chk\n")
                com_file.write("#p b3lyp/def2tzvp geom=check\n\n")
                com_file.write("Ground State Energy Right After Transition\n\n")
                com_file.write("0 1\n")
            elif calculation_state == "ES_Ver":
                # Excited State Verification Calculation
                com_file.write(f"%Mem={memory_gb}GB\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%oldchk={molecule_name}_GS_Opt.chk\n")
                com_file.write(f"%chk={molecule_name}_ES_Ver.chk\n")
                com_file.write("#p b3lyp/def2tzvp TD=(nstates=2, Root=1) geom=check\n\n")
                com_file.write("Excited State Energy Right After Transition\n\n")
                com_file.write("0 1\n")
            elif calculation_state == "ABS":
                # ABS Calculation
                com_file.write(f"%chk={molecule_name}_GS_Opt.chk\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%mem={memory_gb}GB\n")
                com_file.write("#p B3LYP/def2tzvp Freq=(ReadFC, FC, ReadFCHT) geom=check guess=read NoSymm\n\n")
                com_file.write("Franck-Condon Analysis\n\n")
                com_file.write("0 1\n\n")
                com_file.write(f"SpecHwHm=250 SpecRes=20 InpDEner={delta_e:.6f}\n\n")
                com_file.write(f"{molecule_name}_ES_Opt.chk\n\n")
            elif calculation_state == "EMI":
                # EMI Calculation
                com_file.write(f"%chk={molecule_name}_GS_Opt.chk\n")
                com_file.write(f"%NProcShared={cores}\n")
                com_file.write(f"%mem={memory_gb}GB\n")
                com_file.write("#p B3LYP/def2tzvp Freq=(ReadFC, FC, ReadFCHT, Emission) geom=check guess=read NoSymm\n\n")
                com_file.write("Franck-Condon Analysis\n\n")
                com_file.write("0 1\n\n")
                com_file.write(f"SpecHwHm=250 SpecRes=20 InpDEner={delta_e:.6f}\n\n")
                com_file.write(f"{molecule_name}_ES_Opt.chk\n\n")

    except OSError as e:
        print(f"Error writing to file {com_filename}: {e}")
        return

    # Make the .sh script executable
    os.chmod(sh_filename, 0o755)

    print(f"Scripts '{sh_filename}' and '{com_filename}' have been created successfully in {target_dir}.")

create_pbs_and_com_scripts()
