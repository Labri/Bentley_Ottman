"""
adjust points coordinates in O(1).
(also hashes together nearby points)
"""
from geo.point import Point

# how much to we adjust ?
PRECISION = 7
PRECISION_FORMAT = "{{0:.{}f}}".format(PRECISION)

def _coordinate_key(coordinate, wanted_precision=PRECISION):
    """
    return string display of given coordinate with wanted precision.
    """
    if wanted_precision == PRECISION:
        used_format = PRECISION_FORMAT
    else:
        used_format = "{{0:.{}f}}".format(wanted_precision)

    key = used_format.format(coordinate)
    if float(key) == 0.0:  # change any eventual -0 to +0
        key = used_format.format(0.0)
    return key

def _displaced_coordinate_key(coordinate, wanted_precision=PRECISION):
    """
    return string display of given coordinate
    displaced by half precision.
    """
    wanted_limit = 5.0 * 10**(-wanted_precision+1)
    return _coordinate_key(coordinate + wanted_limit, wanted_precision)

class CoordinatesHash(object):
    """
    a CoordinatesHash is structure providing a very fast way (O(1)) of
    merging nearby coordinates in points.
    when initializing a new hash you need to provide the dimension of the space
    and a wanted_precision.

    we ensure that :
        - if any two coordinates have a difference less than
        0.5*10**-wanted_precision then they will be merged to the value of the
        most ancient in the hash.
    """
    #pylint: disable=too-few-public-methods
    def __init__(self, wanted_precision=PRECISION, dimension=2):
        # we need 2*dimension hashes to test
        # displaced and non displaced keys
        self.hashes = [{} for _ in range(2*dimension)]
        self.precision = wanted_precision
        self.fast_hash = set()  # fast test for exact match

    def hash_point(self, point):
        """
        add a point to the hash, returning new point with adjusted coordinates.
        """
        if point in self.fast_hash:
            return point

        new_coordinates = [self.__hash_coordinate(c, i) for i, c in enumerate(point.coordinates)]
        new_point = Point(new_coordinates)

        self.fast_hash.add(new_point)
        return new_point

    def __hash_coordinate(self, coordinate, index=0):
        """
        add 1 coordinate (given index) to the hash, adjusting it if needed.
        """
        key = _coordinate_key(coordinate, self.precision)
        displaced_key = _displaced_coordinate_key(coordinate, self.precision)
        if key in self.hashes[2*index]:
            return self.hashes[2*index][key]
        if displaced_key in self.hashes[2*index+1]:
            return self.hashes[2*index+1][displaced_key]

        self.hashes[2*index][key] = coordinate
        self.hashes[2*index+1][displaced_key] = coordinate
        return coordinate
