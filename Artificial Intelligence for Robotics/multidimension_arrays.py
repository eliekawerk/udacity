
array1d = ["{}".format(col) for col in range(5)]

for row in array1d:
    print row

print "\n"

array2d = [["{},{}".format(row, col) for col in range(6)] for row in range(5)]

for row in array2d:
    print row
    
print "\n"

array3d = [[["{},{},{}".format(row, col, orientation) for col in range(6)] for row in range(5)] for orientation in range(4)]

for orientation in array3d:
    for row in orientation:
        print row
    
print "\n"