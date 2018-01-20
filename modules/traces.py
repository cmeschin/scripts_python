#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module permettant de tracer l'exécution dans un log et dans la console
source: http://sametmax.com/ecrire-des-modules-en-python/
Usage:  logger.info('Hello')
        logger.warning('Testing %s', 'foo')
"""

import logging

from logging.handlers import RotatingFileHandler


# création de l'objet logger qui va nous servir à écrire dans les modules
logger = logging.getLogger()

# on met le niveau du logger à DEBUG, comme ça il écrit tout
logger.setLevel(logging.DEBUG)


# création d'un formateur qui va ajouter le temps, le niveau
# de chaque message quand on écrira un message dans le log
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# création d'un handler qui va rediriger une écriture du log vers
# un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
file_handler = RotatingFileHandler('./log/__name__.log', 'a', 1000000, 1)
# on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
# créé précédement et on ajoute ce handler au logger
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# création d'un second handler qui va rediriger chaque écriture de log
# sur la console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

if __name__ == '__main__':
    print("Module de modules")
    logger.info('youpi')