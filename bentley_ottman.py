#!/usr/bin/env python3
#pylint: disable = R0912, R0914, R0915,
#>>> Fonction  bentley_ottmann trop longue
#pylint: disable = W0512
#>>> Encodage ascii
#pylint: disable = W0601
#>>> Problème avec la variable COUPE
"""
Programme principal du projet
"""

import sys
from heapq import heapify, heappop, heappush
from sortedcontainers import SortedList
from geo.segment import Segment, load_segments
from geo.tycat import tycat

def bentley_ottmann(filename, nodisp=False, noinfo=False):
    """
    Fonction principale de notre projet
    """
    global COUPE
    COUPE = 0
    y_cour = None
    adjuster, segments = load_segments(filename)
    actifs = SortedList()
    evenements = [] #liste de nos evenements, valeurs des y, que lon transformera en Tas ensuite
    pt_inter = {} #dictionnaire que lon retournera a la fin, associant les segments interseptés
    index = 0
    cache_inters = {} #cache qui nous dira si on a deja compare 2 seg
    intersections = [] #liste contenant tous nos points dintersections

    for seg in segments:
        #initialisation de nos evenements
        (x_0, y_0) = seg.endpoints[0].coordinates
        (x_1, y_1) = seg.endpoints[1].coordinates
        Segment.y_cour = [x_0, y_0]
        if y_0 < y_1: #Segments croissant suivant les y
            evenements.append([y_0, -x_0, seg, 'D'])
            evenements.append([y_1, -x_1, seg, 'F'])
        elif y_0 > y_1: #Segments decroissant suivant les y:
            evenements.append([y_0, -x_0, seg, 'F'])
            evenements.append([y_1, -x_1, seg, 'D'])
        else: #Cas d'un segment horizontal
            evenements.append([y_1, -min(x_0, x_1), seg, max(x_0, x_1)])

        pt_inter[seg] = [] #Initialisation du dictionnaire
        cache_inters[seg] = []

    heapify(evenements) #Tas des evenement,3 types, 'D' 'F' 'I': Debut, fin, intersection
    #trié en fonction des y croissant, puis des x décroissants.

    def indice(seg):
        """
        Retourne l'indice de seg dans la liste actifs, None si le segment n'est
        pas présent. Cette fonction auxiliaire est implémentée suite aux
        problèmes majeurs rencontrés avec la méthode index de la classe
        SortedList
        """
        for i, elmt in enumerate(actifs):
            if seg is elmt:
                return i

    def intersection(seg, seg_2):
        """
        Fonction qui va légitimer et gérer l'intersection entre 2 segments
        donnés.
        """
        global COUPE
        if seg_2 not in cache_inters[seg]:  #On ne compare pas deux segments
                                            #déja comparés
            intersection = seg.intersection_with(seg_2)
            cache_inters[seg].append(seg_2)
            cache_inters[seg_2].append(seg)
            if intersection is not None:
                intersection = adjuster.hash_point(intersection) #Ajustement
                if intersection not in seg.endpoints or intersection not in seg_2.endpoints:
                    #Le point nest pas lextrémitié des deux segments
                    pt_inter[seg].append(seg_2)
                    pt_inter[seg_2].append(seg)
                    heappush(evenements, [intersection.coordinates[1],
                                          -intersection.coordinates[0],
                                          seg, 'I', seg_2])
                    #L'ordre dans le tuple est important: il permet de savoir
                    #qui est à gauche ou à droite
                    if intersection not in intersections:
                        intersections.append(intersection)
                    COUPE += 1
        return

    while evenements: #Boucle traitant tous les évènements tant que notre tas
                      #n'est pas vide.
        y_cour = heappop(evenements)
        if y_cour[3] == 'D': #evenement de debut de segment
            Segment.y_cour = [- y_cour[1], y_cour[0]]
            actifs = SortedList(actifs) #Mise à jour de actifs
            seg = y_cour[2]
            actifs.add(seg) #Ajout du nouveau segment aux actifs
            if len(actifs) > 1: #Si un seul segment dans actifs: on ne fait rien
                try:
                    index = actifs.index(seg)
                except ValueError:
                    index = indice(seg)
                if index != len(actifs) - 1:
                    seg_2 = actifs[index + 1]
                    intersection(seg, seg_2)
                if index != 0:
                    seg_2 = actifs[index - 1]
                    intersection(seg_2, seg)


        elif y_cour[3] == 'F': #evenement de fin de segment
            Segment.y_cour = [-y_cour[1], y_cour[0]]
            actifs = SortedList(actifs) #Mise à jour de actifs
            seg = y_cour[2]
            try:
                index = actifs.index(seg)
            except ValueError:
                index = indice(seg)
            actifs.pop(index)

            actifs = SortedList(actifs) #Mise à jour de actifs
            if len(actifs) > 1:
                if 0 < index < len(actifs): #On n'enleve pas le seg le plus à
                                            #droite/gauche
                    seg = actifs[index]
                    seg_2 = actifs[index - 1]
                    intersection(seg, seg_2)

        elif y_cour[3] == 'I': #evenement de point d'intersection
            seg, seg_2 = y_cour[2], y_cour[4]
            try:
                actifs.remove(seg)
            except ValueError:
                index = indice(seg)
                if index is not None: #Renvoie parfois une erreur:
                                      #"segment not in actifs"
                    del actifs[index]
            try:
                actifs.remove(seg_2)
            except ValueError:
                index_2 = indice(seg_2)
                if index_2 is not None:
                    del actifs[index_2]

            Segment.y_cour = [-y_cour[1], y_cour[0] + 0.00000000001]
                            #Cf. convention: A une intersection, on se situe
                            #au dessus de l'intersection
            actifs = SortedList(actifs) #Mise à jour de actifs
            actifs.add(seg) #Une fois changés de place l'intersection passée,
                            #on remet nos deux segments dans actifs
            actifs.add(seg_2)
            try:
                index = actifs.index(seg) #Indice du seg a droite une fois
                                      #l'intersection faite
            except ValueError:
                index = indice(seg)

            if len(actifs) > 2: #On teste les nouvelles intersections possibles
                if index < len(actifs)-1: #Cas de l'extrémité droite de actifs
                    seg_2 = actifs[index + 1]
                    intersection(seg, seg_2)
                if index - 1 != 0:        #Cas de l'extrémité gauche
                    seg_2 = actifs[index-2]
                    intersection(seg_2, y_cour[4])

        else: #Cas dun segment horizontal
            seg_h = y_cour[2]
            for seg in actifs:
                inter = seg_h.intersection_with(seg)
                if inter:
                    inter = adjuster.hash_point(inter)
                    if inter not in seg_h.endpoints or inter not in seg.endpoints:
                        #Le point n'est pas l'extrémité ds deux segments
                        pt_inter[seg_h].append(seg)
                        pt_inter[seg].append(seg_h)
                        if inter not in intersections:
                            intersections.append(inter)
                        COUPE += 1
    if nodisp and noinfo :
        return pt_inter, intersections
    if noinfo:
        tycat(segments, intersections)
        return pt_inter, intersections
    if nodisp:
        print("Le nombre d'intersections (= le nombre de points differents) est : ",
              len(intersections))
        print("Le nombre de coupes est : ", COUPE)
        return pt_inter, intersections
    print("le nombre d'intersections (= le nombre de points differents) est : ",
          len(intersections))
    print("le nombre de coupes est : ", COUPE)


def main():
    """
    Lance test sur tous les fichiers passés en argument
    """
    help_message = """
              Algorithme de Bentley - Ottmann

              Ce programme renvoie un dictionnaire contenant les listes des
              segments interceptant un segment en clé, ainsi que la liste des
              points d'intersections.

              Utilisation :
              ./bo.py [options] [fichiers]

              Options:
              -h, --help    Renvoie ce message d'aide
              --nodisp      Bloque l'affichage de la figure
              --noinfo      Le programme n'affichera pas les informations textuelles

              Fichiers:
              Les fichiers attendus sont sous le format .bo
              """
    if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        sys.stdout.write(help_message)
        return
    nodisp = '--nodisp' in sys.argv[1:]
    noinfo = '--noinfo' in sys.argv[1:]
    for filename in sys.argv[1+int(nodisp)+int(noinfo):]:
        bentley_ottmann(filename, nodisp, noinfo)

main()
