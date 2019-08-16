import numpy as np

def gaussJordan(x, y):
    x = np.linalg.inv(x)
    res = np.dot(x, y)
    return res

def reduce_eqns(x, y):
    np.dot(x.transpose(), x), np.dot(x.transpose(), y)

def get_geo_coordinates(x, y, z):
    '''
    Converts cartesian coordinates to geographical coordinates.

    :param x: Latitude in metres
    :param y: Longitude in metres
    :param z: Altitude in metres
    :type x: Float
    :type y: Float
    :type z: Float
    :return: Latitude, longitude, altitude in geographic coordinates.
    :rtype: Float
    '''
    R = np.sqrt(x**2 + y**2 + z**2)
    lat = np.arcsin(z / R)
    lon = np.arctan2(y, x)

    return np.rad2deg(lon), np.rad2deg(lat), R


def trilaterate(x1,y1,r1,x2,y2,r2,x3,y3,r3):
  A = 2*x2 - 2*x1
  B = 2*y2 - 2*y1
  C = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
  D = 2*x3 - 2*x2
  E = 2*y3 - 2*y2
  F = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2
  x = (C*E - F*B) / (E*A - B*D)
  y = (C*D - A*F) / (B*D - A*E)
  x, y, z = get_geo_coordinates(x, y, 4950497.0726876855)
  return x, y

# if __name__ == '__main__':
#     main(3929701.227678321, 800876.9938873331, 0.000139032461596068, 3934847.309008474, 805486.4460691657, 0.000158007790081513, 3926610.7726530805, 814829.7818535069, 0.000184164305903299)
