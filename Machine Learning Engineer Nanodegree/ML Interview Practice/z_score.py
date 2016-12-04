import math

pc = 20 / 100.
nc = 100

p = 15 / 70.
n = 70


z = (p - pc) / math.sqrt (((p * (1-p)) / n) + ((pc * (1-pc)) / nc))

print z