#!/usr/bin/python
# Generate absorbance data and save testing file for A->B
import random
from numpy import matrix, matlib
import csv

def frange(start, end=None, inc=None):
    "A range function, that does accept float increments..."
    
    if end == None:
        end = start + 0.0
        start = 0.0
        
    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
        
    return L

t_0 = matrix(frange(-1e-6, 0, 5e-11)).transpose()
t_1 = matrix(frange(0, 1.9999500e-6, 5e-11)).transpose()
k = [2.2e7, 3.124e7] # rate constant

a_0 = 1e-3 # initial concentration of A
a_1 = 2e-3 # initial concentration of B
c = matlib.empty([t_1.size, 2])
c[:,0] = a_0 * matlib.exp(-k[0] * t_1)
c[:,1] = a_1 * matlib.exp(-k[1] * t_1)

# molar absorption of species A
a = matlib.empty([2, 1])
a[0,0] = 1e3
a[1,0] = 1e3

y_1 = matlib.dot(c, a)
y_1 = y_1.transpose().tolist()[0]
y_1 = map(lambda y: y + (0.04 * random.random() - 0.02), y_1)

t_0 = t_0.transpose().tolist()[0]
t_1 = t_1.transpose().tolist()[0]

fullLightVoltage = -0.0951192897786
y_1 = map(lambda y:fullLightVoltage*(10**-y), y_1)
y_0 = []
for i in range(0, len(t_0)):
    y_0.append(fullLightVoltage + 0.01 * random.random() - 0.005)

y = y_0 + y_1
t = t_0 + t_1

writer = csv.writer(open('ab_cd.csv', 'w'), delimiter=',', quotechar='"')
writer.writerow(["Record Length", len(y), "Points", 1, 2])
writer.writerow(["Sample Interval", 0])
writer.writerow(["Trigger Point"])
writer.writerow(["Trigger Time"])
writer.writerow([""])
writer.writerow(["Horizontal Offset"])
for i in range(0, len(y)):
    writer.writerow(["", "", "", t[i], y[i]])
