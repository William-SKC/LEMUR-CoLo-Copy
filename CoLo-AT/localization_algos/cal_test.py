
import scipy
import numpy as np
from sympy import *
'''
# for absolute landmark
x_symbol, y_symbol = symbols('x y')
h1 = sqrt((lx-x_symbol)*(lx-x_symbol)+(ly-y_symbol)*(ly-y_symbol))
h2 = atan2((ly-y_symbol), (lx-x_symbol))

h_11 = diff(h1, x_symbol)
print(h_11)
h_12 = diff(h1, y_symbol)
print(h_12)
h_21 = diff(h2, x_symbol)
print(h_21)
h_22 = diff(h2, y_symbol)
print(h_22)
'''
'''
h11 = float(h_11.subs([(x_symbol, x),(y_symbol, y)]))
h12 = float(h_12.subs([(x_symbol, x),(y_symbol, y)]))
h21 = float(h_21.subs([(x_symbol, x),(y_symbol, y)]))
h22 = float(h_22.subs([(x_symbol, x),(y_symbol, y)]))
'''

# for relative landmark
x_i, y_i, x_j, y_j = symbols('x_i, y_i, x_j, y_j')

h1 = sqrt((x_j-x_i)*(x_j-x_i)+(y_j-y_i)*(y_j-y_i))
h2 = atan2((y_j-y_i), (x_j-x_i))

h_11 = diff(h1, x_j)
print(h_11)
h_12 = diff(h1, y_j)
print(h_12)
h_21 = diff(h2, x_j)
print(h_21)
h_22 = diff(h2, y_j)
print(h_22)


temp = np.asmatrix(scipy.linalg.sqrtm(np.matrix('1,2;3,4')))**2
print(temp)
