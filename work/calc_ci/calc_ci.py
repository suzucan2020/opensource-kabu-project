for x in range(1):
    print("|{:9}|".format(1), end="")
    for y in range(8):
        print("{:9}|".format(((y+1)*12)), end="")
print("")

for x in range(1):
    print("|{:9}|".format("---:"), end="")
    for y in range(8):
        print("{:9}|".format("---:"), end="")
print("")
 

profit = 1
for x in range(10):
    profit += 0.01
    print("|{:8.2f}%|".format(profit), end="")
    for y in range(8):
        # print(profit, "**", "month =", ((y+1)*12))
        print("{:8.2f}%|".format(profit**((y+1)*12)), end="")
    print("")
    # print("-")
