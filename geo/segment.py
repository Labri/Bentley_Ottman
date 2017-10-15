"""
segment between two points.
"""
import struct
from math import pi, atan
from geo.point import Point
from geo.quadrant import Quadrant
from geo.coordinates_hash import CoordinatesHash

class Segment(object):
    """
    oriented segment between two points.

    for example:

    - create a new segment between two points:

        segment = Segment([point1, point2])

    - create a new segment from coordinates:

        segment = Segment([Point([1.0, 2.0]), Point([3.0, 4.0])])

    - compute intersection point with other segment:

        intersection = segment1.intersection_with(segment2)

    """
    cache_x = dict() # dictionnaire de nos valeurs de clefs
    y_cour = [0, 0]

    def __init__(self, points):
        """
        create a segment from an array of two points.
        """
        self.endpoints = points

    def __lt__(self, other):
        """
        comparison relation given by clefs function
        """
        cle0, cle1 = self.clefs(), other.clefs()
        return (cle0[0] < cle1[0]) or (cle0[0] == cle1[0] and cle0[1] < cle1[1])

    def clefs(self):
        """
        allows the comparison between two segments as specificated
        """
        try:
            if Segment.y_cour[0] > Segment.cache_x[(self, Segment.y_cour[1])][0]:
                Segment.cache_x[(self, Segment.y_cour[1])][1] =\
                    -Segment.cache_x[(self, Segment.y_cour[1])][1]
            return Segment.cache_x[(self, Segment.y_cour[1])]
        except KeyError:
            pass
        pos = (Segment.y_cour[0], Segment.y_cour[1])
        x_a, y_a = self.endpoints[0].coordinates
        x_b, y_b = self.endpoints[1].coordinates
        if x_a == x_b: #Cas d'un segment vertical
            x_p = x_a
            angle = pi / 2
        elif y_a == y_b: #Cas d'un segment horrizontal
            x_p, angle = x_a, 0
        else:
            cdir = (y_b - y_a) / (x_b - x_a)
            ord_or = y_b - cdir * x_b
            angle = (pi - atan((y_b - y_a) / (x_b - x_a))) % 2 * pi
            x_p = (pos[1] - ord_or) / cdir
        if x_p > pos[0]:
            Segment.cache_x[(self, Segment.y_cour[1])] = [x_p, angle]
        else:
            Segment.cache_x[(self, Segment.y_cour[1])] = [x_p, - angle]
        return Segment.cache_x[(self, Segment.y_cour[1])]

    def copy(self):
        """
        return duplicate of given segment (no shared points with original,
        they are also copied).
        """
        return Segment([p.copy() for p in self.endpoints])

    def length(self):
        """
        return length of segment.
        example:
            segment = Segment([Point([1, 1]), Point([5, 1])])
            distance = segment.length() # distance is 4
        """
        return self.endpoints[0].distance_to(self.endpoints[1])

    def bounding_quadrant(self):
        """
        return min quadrant containing self.
        """
        quadrant = Quadrant.empty_quadrant(2)
        for point in self.endpoints:
            quadrant.add_point(point)
        return quadrant

    def svg_content(self):
        """
        svg for tycat.
        """
        return '<line x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(
            self.endpoints[0].coordinates[0], self.endpoints[0].coordinates[1],
            self.endpoints[1].coordinates[0], self.endpoints[1].coordinates[1])

    def intersection_with(self, other):
        """
        intersect two 2d segments.
        only return point if included on the two segments.
        """
        i = self.line_intersection_with(other)
        if i is None:
            return  # parallel lines

        if self.contains(i) and other.contains(i):
            return i

    def line_intersection_with(self, other):
        """
        return point intersecting with the two lines passing through
        the segments.
        none if lines are almost parallel.
        """
        # solve following system :
        # intersection = start of self + alpha * direction of self
        # intersection = start of other + beta * direction of other
        directions = [s.endpoints[1] - s.endpoints[0] for s in (self, other)]
        denominator = directions[0].cross_product(directions[1])
        if abs(denominator) < 0.000001:
            # almost parallel lines
            return
        start_diff = other.endpoints[0] - self.endpoints[0]
        alpha = start_diff.cross_product(directions[1]) / denominator
        return self.endpoints[0] + directions[0] * alpha

    def contains(self, possible_point):
        """
        is given point inside us ?
        be careful, determining if a point is inside a segment is a difficult problem
        (it is in fact a meaningless question in most cases).
        you might get wrong results for points extremely near endpoints.
        """
        distance = sum(possible_point.distance_to(p) for p in self.endpoints)
        return abs(distance - self.length()) < 0.000001

    def __str__(self):
        return "Segment([" + str(self.endpoints[0]) + ", " + \
            str(self.endpoints[1]) + "])"

    def __repr__(self):
        return "[" + repr(self.endpoints[0]) + ", " + \
            repr(self.endpoints[1]) + "])"


def load_segments(filename):
    """
    loads given .bo file.
    returns a vector of segments.
    """
    coordinates_struct = struct.Struct('4d')
    segments = []
    adjuster = CoordinatesHash()

    with open(filename, "rb") as bo_file:
        packed_segment = bo_file.read(32)
        while packed_segment:
            coordinates = coordinates_struct.unpack(packed_segment)
            raw_points = [Point(coordinates[0:2]), Point(coordinates[2:])]
            adjusted_points = [adjuster.hash_point(p) for p in raw_points]
            segments.append(Segment(adjusted_points))
            packed_segment = bo_file.read(32)

    return adjuster, segments
