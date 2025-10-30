#Create a list of tuples that are percentiles and Household Incomes at the specified percentiles for the following table:

#Percentile    	Income
#10      		14629
#20      		25600
#30      		37002
#40      		50000
#50      		63179
#60      		79542
#70      		100162
#80      		130000
#90      		184292

# Create a list of tuples (percentile, income)

import numpy as np

hh_income = [
	(10, 14629),
	(20, 25600),
	(30, 37002),
	(40, 50000),
	(50, 63179),
	(60, 79542),
	(70, 100162),
	(80, 130000),
	(90, 184292),
]


hh_income_array = np.array(hh_income)

#Report dimensions of the array and number of elements in the array

print("Dimensions:", hh_income_array.shape)
print("Dimensions v2:", hh_income_array.ndim)
print("Number of elements:", hh_income_array.size)

for i in range(len(hh_income_array)):
    print(hh_income_array[i][0], hh_income_array[i][1])