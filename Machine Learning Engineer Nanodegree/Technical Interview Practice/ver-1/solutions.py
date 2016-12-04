
# Following are my solutions for 5 technical interview practice questions

"""
QUESTION 1: Given two strings s and t, determine whether some anagram of t is a substring of s.
For example: if s = "udacity" and t = "ad", then the function returns True.
Your function definition should look like: question1(s, t) and return a boolean True or False.
"""
# return True if two input strings are equal when sorted
def is_anagram(s1, s2):
    s1 = list(s1)
    s2 = list(s2)
    s1.sort()
    s2.sort()
    return s1 == s2

# search for some anagram of t in s
def find_anagram(s, t):
    
    if s and t:
        pattern_length = len(s)
        match_length = len(t)
        
        for i in range(pattern_length - match_length + 1):
            if is_anagram(s[i: i + match_length], t):
                return True
        
    return False

# main
def question1(s, t):
    return find_anagram(s, t)

# testcases
print "Answer 1:"

# base testcase
pattern = "udacity"
match = "ad"
answer = question1(pattern, match)  # expect True
print "anagram of '{}' in '{}': {}".format(match, pattern, answer)

# edge testcase-1
pattern = "udacity"
match = "???"
answer = question1(pattern, match)  # expect False
print "anagram of '{}' in '{}': {}".format(match, pattern, answer)

# edge testcase-2
pattern = "udacity"
match = None
answer = question1(pattern, match)  # expect False
print "anagram of {} in '{}': {}".format(match, pattern, answer)

#############################################################################################################

"""
QUESTION 2: Given a string a, find the longest palindromic substring contained in a. Your function 
definition should look like question2(a), and return a string.
"""
# find palindrom by looking at all of the possible substrings and checking them individually
def find_palindromes(s):
    
    palindromes = []
    
    if s:
        s = s.lower()
        for i in range(len(s)):
            for j in range(0, i):
                chunk = s[j:i + 1]
                if chunk == chunk[::-1]:
                    palindromes.append(chunk)

    if palindromes:
        return max(palindromes, key=len)
    else:
        return None

# main
def question2(a):
    return find_palindromes(a)

# testcases
print "\nAnswer 2:"

# base testcase
text = "abbaabba???"
answer = question2(text) # expect abbaabba
print "longest palindrome in '{}': '{}'".format(text, answer)

# edge testcase-1
text = "abc"
answer = question2(text) # expect None
print "longest palindrome in '{}': {}".format(text, answer)

# edge testcase-2
text = None
answer = question2(text) # expect None
print "longest palindrome in {}: {}".format(text, answer)

#############################################################################################################

"""
QUESTION 3: Given an undirected graph G, find the minimum spanning tree within G. A minimum spanning 
tree connects all vertices in a graph with the smallest possible total weight of edges. 
Your function should take in and return an adjacency list structured like this:

{'A': [('B', 2)],
 'B': [('A', 2), ('C', 5)], 
 'C': [('B', 5)]}
 
Vertices are represented as unique strings. The function definition should be question3(G)

Gained intuitions from these videos:
Disjoint Sets : https://www.youtube.com/watch?v=UBY4sF86KEY
Kruskal Algorithm : https://www.youtube.com/watch?v=5xosHRdxqHA
"""
parent = {}
rank = {}

# initialize disjoint sets. each set contains one vertice. rank is used to keep the 
# tree MST flat as much as possible for faster search.
def make_set(vertice):
    parent[vertice] = vertice
    rank[vertice] = 0

# find the set to which this vertice belongs
def find(vertice):
    if parent[vertice] != vertice:
        parent[vertice] = find(parent[vertice])
    return parent[vertice]

# merge the sets represented by these two given root nodes
def union(vertice1, vertice2):
    root1 = find(vertice1)
    root2 = find(vertice2)
    if root1 != root2:
        if rank[root1] > rank[root2]:
            parent[root2] = root1
        else:
            parent[root1] = root2
            if rank[root1] == rank[root2]: rank[root2] += 1

# perform kruskal algorithm to find mst
def kruskal(vertices, edges):
    minimum_spanning_tree = set()
    for vertice in vertices:
        make_set(vertice)

    # sort edges by increasing weights
    edges = sorted(edges, key=lambda x : x[2])
    
    for edge in edges:
        vertice1, vertice2, wt = edge
        if find(vertice1) != find(vertice2):
            union(vertice1, vertice2)
            minimum_spanning_tree.add(edge)
            
    return minimum_spanning_tree

# main
def question3(G):
    
    graph = G
    vertices = []
    edges = []
    
    # pre process given input graph and extract all vertices and edges
    for vertice in graph.keys():
        # collect vertices
        vertices.append(vertice)
        # build edge tuples
        verticeEdges = graph[vertice]
        for verticeEdge in verticeEdges:
            fromNode = vertice
            toNode, weight = verticeEdge
            edges.append((fromNode, toNode, weight))
        
    # perform Kruskal algo
    ms_tree = kruskal(vertices, edges)
    
    # post process results into the required output format
    output = {}
    for node in ms_tree:
        fromNode, toNode, weight = node
        
        if toNode < fromNode:
            fromNode = node[1]
            toNode = node[0]
            
        if fromNode in output:
            output[fromNode].append((toNode, weight))
        else:
            output[fromNode] = [(toNode, weight)]
            
    return output

# testcases
print "\nAnswer 3:"
import pprint
pp = pprint.PrettyPrinter()

# base testcase
G = {'A': [('B', 1), ('C', 7)],
     'B': [('A', 1), ('C', 5), ('D', 3), ('E', 4)],
     'C': [('A', 7), ('B', 5), ('D', 6)],
     'D': [('B', 3), ('C', 6), ('E', 2)],
     'E': [('B', 4), ('D', 2)],
    }
print "Graph-1:"
pp.pprint(G)
answer = question3(G) # expect {'A': [('B', 1)], 'B': [('C', 5), ('D', 3)], 'D': [('E', 2)]}
print "Minimum Spanning Tree:", answer

# edge testcase-1
G = {'A': [('B', 1), ('C', 1)],
     'B': [('A', 1), ('C', 1)],
     'C': [('A', 1), ('B', 1)],
    }
print "Graph-2:"
pp.pprint(G)
answer = question3(G) # expect {'A': [('C', 1), ('B', 1)]}
print "Minimum Spanning Tree:", answer

# edge testcase-2
print "Graph-3:"
G = {}
pp.pprint(G)
answer = question3(G) # expect {}
print "Minimum Spanning Tree:", answer

#############################################################################################################

"""
QUESTION 4: Find the least common ancestor between two nodes on a binary search tree. The least 
common ancestor is the farthest node from the root that is an ancestor of both nodes. 
For example, the root is a common ancestor of all nodes on the tree, but if both nodes 
are descendents of the root's left child, then that left child might be the lowest 
common ancestor. You can assume that both nodes are in the tree, and the tree itself 
adheres to all BST properties. The function definition should look like question4(T, r, n1, n2), 
where T is the tree represented as a matrix, where the index of the list is equal to the 
integer stored in that node and a 1 represents a child node, r is a non-negative integer 
representing the root, and n1 and n2 are non-negative integers representing the two nodes 
in no particular order. 
"""
# find LCA of two nodes n1 and n2
 
# binary tree node
class Element:
 
    # Constructor to create a new node
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        
    def children(self):
        return [self.left, self.right]
    
    def show(self):
        l = self.left.value if (self.left) else None
        r = self.right.value if (self.right) else None
        print "{} -> {}, {}".format(self.value, l, r)
        
# binary search tree
class BST(object):
    
    # init tree
    def __init__(self, root):
        self.root = Element(root)
        
    # insert new node in the tree
    def insert(self, new_val):
        self.insert_helper(self.root, new_val)
        
    # find the correct location for the new node in the tree
    def insert_helper(self, current, new_val):
        if current.value < new_val:
            if current.right:
                self.insert_helper(current.right, new_val)
            else:
                current.right = Element(new_val)
        else:
            if current.left:
                self.insert_helper(current.left, new_val)
            else:
                current.left = Element(new_val)

    def show(self):
        self.root.show()
        children = self.root.children()
        while(len(children) > 0):
            child = children.pop(0)
            if child:
                child.show()
                children = children + child.children()
                
# build tree recursively from T matrix
def buildTree(tree, node): 
    if T and node in T:
        children = T[node]
        for index, child in enumerate(children):
            if child == 1:
                tree.insert(index)
                buildTree(tree, index)
            
# find LCA of n1 and n2
def lca(root, n1, n2):
     
    # base case
    if root is None:
        return None
 
    # if both n1 and n2 are smaller than root, then LCA lies in left
    if(root.value > n1 and root.value > n2):
        return lca(root.left, n1, n2)
 
    # if both n1 and n2 are greater than root, then LCA lies in right 
    if(root.value < n1 and root.value < n2):
        return lca(root.right, n1, n2)
 
    return root

# main
def question4(T, r, n1, n2):
    
    # Set up tree
    tree = BST(r)
    buildTree(tree, r)
    
    # find lca
    return lca(tree.root, n1, n2)

# testcases
print "\nAnswer 4:"

# base testcase
T = [[0, 1, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0],
     [1, 0, 0, 0, 1],
     [0, 0, 0, 0, 0]]
r = 3
n1 = 1
n2 = 4
answer = question4(T, r, n1, n2) # expect 3
print "LCA of {} and {} is {}".format(n1, n2, answer.value)

# edge testcase-1
T = T # same as above
r = 3
n1 = 99
n2 = 99
answer = question4(T, r, n1, n2) # expect None
print "LCA of {} and {} is {}".format(n1, n2, answer)

# edge testcase-2
T = None
r = 0
n1 = -1
n2 = -1
answer = question4(T, r, n1, n2) # expect None
print "LCA of {} and {} is {}".format(n1, n2, answer)

#############################################################################################################

"""
QUESTION 5: Find the element in a singly linked list that's m elements from the end. For example, 
if a linked list has 5 elements, the 3rd element from the end is the 3rd element. 
The function definition should look like question5(ll, m), where ll is the first node of 
a linked list and m is the "mth number from the end". You should copy/paste the Node class 
below to use as a representation of a node in the linked list. Return the value of the 
node at that position.
"""
# linked list node
class Node(object):
    def __init__(self, data):
        self.data = data
        self.next = None
   
# linked list 
class LinkedList(object):
    def __init__(self, head=None):
        self.head = head
        
    def append(self, new_node):
        current = self.head
        if self.head:
            while current.next:
                current = current.next
            current.next = new_node
        else:
            self.head = new_node

    """
    Maintain two pointers - reference pointer and main pointer. Initialize both reference and main 
    pointers to head. First move reference pointer to n nodes from head. Now move both pointers one 
    by one until reference pointer reaches end. Now main pointer will point to nth node from the end. 
    Return main pointer.
    """
    def nthNodeFromLast(self, m):
        main_ptr = self.head
        ref_ptr = self.head 
     
        count = 0
        if(self.head is not None):
            while(count < m):
                if(ref_ptr is None):
                    print "ERROR: %d is greater than the no. of nodes in list" % (m)
                    return
  
                ref_ptr = ref_ptr.next
                count += 1
 
        while(ref_ptr is not None):
            main_ptr = main_ptr.next
            ref_ptr = ref_ptr.next
        
        return main_ptr
    
# main
def question5(ll, m):
    if ll:
        return ll.nthNodeFromLast(m)

# testcases
print "\nAnswer 5:"

# base testcase
# setup nodes
n1 = Node(1)
n2 = Node(2)
n3 = Node(3)
n4 = Node(4)
n5 = Node(5)

# setup LinkedList
ll = LinkedList(n1)
ll.append(n2)
ll.append(n3)
ll.append(n4)
ll.append(n5)

m = 3
answer = question5(ll, m) # expect 3
print "node in linked list that is {} steps from the end is {}".format(m, answer.data)

# edge testcase-1
m = 99
answer = question5(ll, m) # expect ERROR: 99 is greater than the no. of nodes in list

# edge testcase-2
ll = None
m = 3
answer = question5(ll, m) # expect None
print "node in linked list that is {} steps from the end is {}".format(m, answer)


