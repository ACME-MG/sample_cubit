file_name = "r2r25_40x_inl617"
with open(f"{file_name}.csv", "r") as file:
    all_lines = file.readlines()
with open(f"{file_name}_compressed.csv", "w") as file:
    for line in all_lines:
        line_list = line.replace("\n", "").split(",")
        if not "NaN" in line_list:
            file.write(line)