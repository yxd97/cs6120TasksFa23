import numpy
import scipy.sparse

# taken from the brili output
rowptr = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,]
colidx = [0,10,20,30,40,1,11,21,31,41,2,12,22,32,42,3,13,23,33,43,4,14,24,34,44,5,15,25,35,45,6,16,26,36,46,7,17,27,37,47,8,18,28,38,48,9,19,29,39,49,10,20,30,40,0,11,21,31,41,1,12,22,32,42,2,13,23,33,43,3,14,24,34,44,4,15,25,35,45,5,16,26,36,46,6,17,27,37,47,7,18,28,38,48,8,19,29,39,49,9,20,30,40,0,10,21,31,41,1,11,22,32,42,2,12,23,33,43,3,13,24,34,44,4,14,25,35,45,5,15,26,36,46,6,16,27,37,47,7,17,28,38,48,8,18,29,39,49,9,19,30,40,0,10,20,31,41,1,11,21,32,42,2,12,22,33,43,3,13,23,34,44,4,14,24,35,45,5,15,25,36,46,6,16,26,37,47,7,17,27,38,48,8,18,28,39,49,9,19,29,40,0,10,20,30,41,1,11,21,31,42,2,12,22,32,43,3,13,23,33,44,4,14,24,34,45,5,15,25,35,46,6,16,26,36,47,7,17,27,37,48,8,18,28,38,49,9,19,29,39,]
values = [5,0,1,2,5,0,1,3,6,2,5,0,1,3,6,2,4,8,6,3,7,5,0,1,3,6,3,7,5,1,3,7,5,0,0,1,-3,0,0,0,-5,6,3,0,0,7,-1,5,0,0,-6,5,-6,5,-6,-1,-1,5,-5,7,4,-8,0,-6,5,-6,5,-6,5,-6,-2,3,7,-1,4,-7,-4,8,6,3,6,2,-1,-1,-1,5,-6,-1,4,-8,-6,-1,-1,-1,-2,-3,1,3,0,0,6,2,4,-7,2,-2,2,5,-5,-9,-7,2,4,9,-7,3,0,7,-1,-1,-2,-4,-7,2,5,1,2,-1,4,-7,3,-9,9,8,-9,-7,-3,0,-5,6,3,7,-1,4,8,0,0,-9,-7,3,-9,8,7,5,-6,-1,-2,2,-1,-2,-3,0,1,2,4,9,-8,0,1,2,-1,-2,-3,-5,6,2,-1,-1,-2,2,-2,-4,-7,3,6,-3,1,-3,-6,4,-8,0,-5,-9,-8,-5,7,-1,-2,-3,1,-4,8,-9,-8,-5,7,5,0,1,-3,-5,-9,-8,1,-4,-7,3,0,6,3,-9,9,-7,2,-2,2,4,-7,3,7,-1,4,-8,1,-3,-6,5,0,-5,0,7,4,9,8,-9,-7,2,-2,-3,]
vec = [3,7,5,1,2,4,8,6,3,6,3,6,3,6,2,5,0,1,2,5,0,0,0,1,2,4,9,9,8,7,5,0,0,1,2,5,-5,7,-2,3,6,3,0,0,-9,8,-9,9,-8,-6,]
res = [55,12,25,40,-1,100,69,3,21,72,-36,28,37,-43,33,49,24,-68,-16,1,19,-74,24,-4,65,-13,55,-108,46,27,39,2,11,17,12,-4,44,0,-81,-94,-22,64,-52,17,-37,-1,-148,-93,85,-1,]

nrows = 50
ncols = 50

matrix = scipy.sparse.csr_matrix(
    (values, colidx, rowptr),
    shape = (nrows, ncols)
)

vector = numpy.array(vec)
result = numpy.array(res)

reference = matrix @ vector

for i in range(nrows):
    correct = True
    if reference[i] != result[i]:
        print(f'Error! Mismatch at the {i}-th element!')
        print(f'  Expected: {reference[i]}')
        print(f'    Actual: {result[i]}')
        correct = False

if correct:
    print("Test Passed!")
else:
    print("Test Failed!")

