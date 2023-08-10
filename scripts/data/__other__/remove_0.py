file = open("p91b.csv", "r")
all_lines = file.readlines()
file.close()

file = open("p91b_new.csv", "w+")
for line in all_lines:
    file_list = line.replace("\n", "").split(",")
    if file_list[3] != "0":
        file.write(line)
file.close()