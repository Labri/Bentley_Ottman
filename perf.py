#!/usr/bin/env python3
#pylint: disable = W0512
#>>> Encodage ascii
"""
Programme permettant d'établir une comparaison de performances
"""
import sys
import time
from bo import bentley_ottmann
from naif import naif
from geo.segment import load_segments
def main():
    """
    Fonction principal testant les performances des deux algorithmes
    (naïf et Bentley Ottman)
    """
    fichier = open("données.txt", "a")
    for filename in sys.argv[1:]:
        time_i = time.time()
        bentley_ottmann(filename)
        time_f = time.time()
        fichier.write(filename +" "+ str(time_f - time_i))
    for filename in sys.argv[1:]:
        time_i = time.time()
        naif(filename)
        time_f = time.time()
        fichier.write(filename + " "+ str(time_f - time_i))
    fichier.close()

# main()

def nb_segments():
    """
    Fonction renvoyant le nombre de segments des fichiers .bo
    """
    fichier = open("données.txt", "a")
    for filename in sys.argv[1:]:
        _, segments = load_segments(filename)
        fichier.write(str(len(segments)) + "\n")

# nb_segments()
