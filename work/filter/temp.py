import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# print(sys.path)
import okap
import myfilter


# input_fname  = "stock-code-list/8man-12man-volume-over40k.txt"
# input_fname  = "stock-code-list/buy-list.txt"
input_fname  = "stock-code-list/up-month.txt"
output_fname = "stock-code-list/filterMACD.txt"
 
year  = 2021
codes = okap.read_stock_code_list(input_fname)

tmp_message = "===========================\nMACD golden cross\n==========================="
print(tmp_message)

tmp_list = []
for code in codes:
    print("START: ", code)
    
    tmp_str = myfilter.MACD_golden_cross(code)

    if tmp_str != "":
        tmp_list.append(tmp_str)

print("==== MACD golden cross ====")
for x in tmp_list:
    print(x)
