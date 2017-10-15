#!/usr/bin/env python3
#pylint: disable = W0512
#>>> Encodage ascii
"""
Programme naif de recherche d'intesrections
"""

import sys
from geo.segment import load_segments
from geo.tycat import tycat

def naif(filename):
    """
    Fonction résolvant le problème de façon intuitive
    """
    coupe = 0
    intersections = []
    adjuster, segments = load_segments(filename)
    for i, seg_i in enumerate(segments):
        for seg_j in segments[i:]:
            inters = seg_i.intersection_with(seg_j)
            if inters is not None:
                inters = adjuster.hash_point(inters)
                if inters not in seg_i.endpoints or inters not in seg_j.endpoints:
                    if inters not in intersections:
                        intersections.append(inters)
                    coupe += 1
    print("le nombre d'intersections est : ", len(intersections))
    print("le nombre de coupes est :", coupe)
    tycat(segments, intersections)
    return intersections



def main():
    """
    Fonction principale
    """
    for filename in sys.argv[1:]:
        naif(filename)

main()
