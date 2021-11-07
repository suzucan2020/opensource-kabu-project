import sys


file_a = sys.argv[1]
file_b = sys.argv[2]

print("Date,code")
# print(file_a, file_b)

with open(file_a) as f:
    list_a = f.readlines()

with open(file_b) as f:
    list_b = f.readlines()

for line_b in list_b:
    flag = 0
    for line_a in list_a:
        if line_b in line_a:
            # print("HIT")
            print(line_a.strip())
            flag = 1
    if flag != 1:
        o_str = "2021-11-04 22:30:00+09:00,{}".format(line_b.strip())
        print(o_str)
        # print(line_b.strip())
