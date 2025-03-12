import os
import re

# Directory
directory = '/gfshome/SpdzT/evaluation'
# directory = '/gfshome/SpdzT/evaluation/baseline-evaluation'
# directory = '/gfshome/SpdzT/evaluation/baseline-evaluation/naive-baseline'
# directory = '/gfshome/SpdzT/evaluation/baseline-evaluation/unitrans-baseline'
# directory = '/gfshome/SpdzT/evaluation/baseline-evaluation/intertrans-baseline'

# Order of the files
file_order = [
    "array_access_traverse_test",
    "for_test",
    "if_test",
    "math_test",
    "numpy_operation_test",
    "numpy_ufunc_test",
    "all_rewrite_test"
]

headers = ['experiment-1-stage_2', 'experiment-1-stage_3']


for header in headers:
    
    files = [f for f in os.listdir(directory) if f.startswith(header) and f.endswith('.txt')]
    
    if not files:
        print(f"No files found for header: {header}")
        continue

    ordered_files = []
    for test_name in file_order:
        for file in files:
            if test_name in file:
                ordered_files.append(file)

    for f in ordered_files:
        print(f)

    if len(ordered_files) != 7:
        raise ValueError(f"Expected 7 files, but found {len(ordered_files)}. Check the filenames.")

    p1_pattern = r"p1_acc\s*:\s*(\d+\.\d+)%"
    p1_percentages = []
    p2_pattern = r"p2_acc\s*:\s*(\d+\.\d+)%"
    p2_percentages = []


    for file in ordered_files:
        file_path = os.path.join(directory, file)
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            last_three_lines = lines[-3:]
            # print(last_three_lines)      
            match = re.search(p1_pattern, last_three_lines[0])
            if match:
                percentage = float(match.group(1)) 
                p1_percentages.append(percentage)
            else:
                p1_percentages.append(None)         
                
            match = re.search(p2_pattern, last_three_lines[1])
            if match:
                percentage = float(match.group(1)) 
                p2_percentages.append(percentage)
            else:
                p2_percentages.append(None)         


    # merge numpy_operation_test and numpy_ufunc_test as numpy
    combined_value = (p1_percentages[4] * 32 + p1_percentages[5] * 34) / 66
    p1_percentages[4] = round(combined_value, 2)  
    del p1_percentages[5]               

    combined_value = (p2_percentages[4] * 32 + p2_percentages[5] * 34) / 66
    p2_percentages[4] = round(combined_value, 2)  
    del p2_percentages[5]               



    # weighted average
    weights = [43, 97, 34, 38, 66, 35]
    weight_sum = sum(weights)

    p1_weighted_sum = sum(p1_percentages[i] * weights[i] for i in range(len(weights)))
    p1_average = round(p1_weighted_sum / weight_sum, 2)
    p1_percentages.append(p1_average)

    p2_weighted_sum = sum(p2_percentages[i] * weights[i] for i in range(len(weights)))
    p2_average = round(p2_weighted_sum / weight_sum, 2)
    p2_percentages.append(p2_average)



    # print(p1_percentages)
    # print(p2_percentages)

    print("\t".join(map(str, p1_percentages)))
    print("\t".join(map(str, p2_percentages)))

