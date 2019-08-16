import numpy as np

def trilaterate(x1, y1, z1, r1, x2, y2, z2, r2, x3, y3, z3, r3):
    P1 = np.array([x1, y1, z1])
    P2 = np.array([x2, y2, z2])
    P3 = np.array([x3, y3, z3])

    ex = (P2 - P1)/(np.linalg.norm(P2 - P1))
    i = np.dot(ex, P3 - P1)
    ey = (P3 - P1 - i*ex)/(np.linalg.norm(P3 - P1 - i*ex))
    ez = np.cross(ex,ey)
    d = np.linalg.norm(P2 - P1)
    j = np.dot(ey, P3 - P1)

    x = (pow(r1,2) - pow(r2,2) + pow(d,2))/(2*d)
    y = ((pow(r1,2) - pow(r3,2) + pow(i,2) + pow(j,2))/(2*j)) - ((i/j)*x)
    z = np.sqrt(pow(r1,2) - pow(x,2) - pow(y,2))

    res = P1 + x*ex + y*ey + z*ez

    return res[0], res[1], res[2]
