# Download
# pip install numpy

import numpy as np

# Arrays
vector_array = np.array([1, 2, 3, 4, 5, 6])

matris_array = np.array([[1, 2, 3], [4, 5, 6]])

zeros_array = np.zeros((2, 3))

ones_array = np.ones((3, 2))

full_array = np.full((2, 2), 7)

array = np.arange(10, 21, 2) #=>[10 12 14 16 18 20]

# Array properties
print(vector_array.shape)  #=>(6,)
print(matris_array.ndim)  #=>2
print(vector_array.dtype)  #=>int64
print(matris_array.size)  #=>6

# Accessing array elements
print(vector_array[0])  #=>1
print(matris_array[1, 2])  #=>6
print(vector_array[1:4])  #=>[2 3 4]
data = array[2:5] = 10 #=>array = [10 12 10 10 10 20]

# Mathematical and statistical operations
print(np.sum(vector_array))  # =>21
print(np.mean(vector_array))  # =>3.5
print(np.std(vector_array))  # =>1.707825127659933
print(np.max(vector_array))  # =>6
print(np.min(vector_array))  # =>1
print(np.var(array)) #=>11.666666666666666
print(np.std(array)) #=>3.415650255319866

# Operations on two arrays
print(vector_array + array)  # =>[11 14 17 20 23 26]
print(vector_array * array)  # =>[10 24 42 64 90 120]

# Transforming the array

print(vector_array.reshape(2,3)) # => [[1 2 3][4 5 6]]
print(matris_array.flatten()) # => [1 2 3 4 5 6]

# Data type conversion
print(array.astype(float).dtype) # =>float64

# Augmentation operation
x = np.array([[1, 2], [3, 4]])
y = np.array([[5, 6]])
print(np.concatenate((x, y), axis=0)) #=>[[1 2][3 4][5 6]]
