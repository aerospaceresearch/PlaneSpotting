import numpy as np

def gaussJordan(x, y):
    x = np.linalg.inv(x)
    res = np.dot(x, y)
    return res

def reduce_eqns(x, y):
    np.dot(x.transpose(), x), np.dot(x.transpose(), y)

def main(): #to be worked upon
    return
