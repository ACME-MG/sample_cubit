"""
 File:          Compressor
 Description:   Compresses large EBSD CSV files
 Author:        Janzen Choi

"""

# Libraries
import time

# Constants
BIG_FILE = "asd.csv"
NEW_FILE = "inl_40x_10m.csv"
SIG_FIGS = 5

# Open both files
big_file = open(BIG_FILE, "r")
new_file = open(NEW_FILE, "w+")

# Extract header information
header = big_file.readline()
header_list = header.replace("\n", "").split(",")
x_index = header_list.index("x")
y_index = header_list.index("y")
phase_id_index = header_list.index("phase_id")
graid_id_index = header_list.index("grain_id")
phi_1_index = header_list.index("phi_1")
Phi_index = header_list.index("Phi")
phi_2_index = header_list.index("phi_2")

# Transfer header
new_file.write("x,y,phase_id,grain_id,phi_1,Phi,phi_2\n")

# Initialise before transfer
x_min, y_min = 0, 0
first_iteration = True
start_time = time.time()

# Transfer the contents of the files with lower resolution
for line in big_file.readlines():
    
    # If coordinates have NaN, then continue
    row_list = line.replace("\n", "").split(",")
    if "NaN" in row_list:
        continue

    # Get coordinates
    if first_iteration:
        x_min = x
        y_min = y
        first_iteration = False
    x = round(float(row_list[x_index]), 2) - x_min
    y = round(float(row_list[y_index]), 2) - y_min
    
    # Extract valid data
    phase_id    = row_list[phase_id_index]
    graid_id    = row_list[graid_id_index]
    phi_1       = row_list[phi_1_index][:SIG_FIGS+1]
    Phi         = row_list[Phi_index][:SIG_FIGS+1]
    phi_2       = row_list[phi_2_index][:SIG_FIGS+1]

    # Add extracted data to new file
    new_file.write(f"{x},{y},{phase_id},{graid_id},{phi_1},{Phi},{phi_2}\n")

# Close both files
big_file.close()
new_file.close()
print(f"x_min: {x_min}")
print(f"y_min: {y_min}")