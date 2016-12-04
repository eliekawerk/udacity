
class Element:
 
    # Constructor to create a new node
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        
 
def question4(T, r, n1, n2):
    pass

#            5
#          /  \
#        /      \
#       3        8
#      / \      / \
#     1   4    7   10
#             /
#            6

    # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0
T = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 0
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 1
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 2
     [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0], # 3
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 4
     [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0], # 5
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 6
     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], # 7
     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1], # 8
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 9
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]] # 10
r = 5
n1 = 6
n2 = 1
answer = question4(T, r, n1, n2) # expect None
print "LCA of {} and {} is {}".format(n1, n2, answer.value)






