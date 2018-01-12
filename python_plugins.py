#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module principal pour les scripts de supervision

Des classes seront créées au fur et à mesure des migrations de scripts actuellement en vbs et bash
"""

import os
import re
from modules.traces import *

#charger le fichier de log d:\Python\tests\supervisorctl.log
# exemple de contenu
#kafka                            BACKOFF   Exited too quickly (process log may have details)
#zookeeper                        RUNNING   pid 24697, uptime 0:25:11

# parcourir le fichier et extraire les 3 colonnes
# ou executer la commande "supervisorctl status" pour avoir les infos
# Give a Json file and return a List
def read_values_from_file(path):
    my_file = open(path,'r')
    my_file.readline()
    print(my_file)
    # for line in re.sub(' +',';',my_file):
    #     process = line.split(';')[0]
    #     statut = line.split(';')[1]
    #     detail=line.split(';')[2]
    #     print(process,statut,detail)

# si colonne 2 == RUNNING alors
#   ok + 1
#   construction du message de sortie OK "process" + "pid et uptime"
# sinon
#   KO + 1
#   construction du message de sortie CRITIQUE "process" + "STATUT" + "message"

read_values_from_file("d:/Python/tests/supervisorctl.log")

if __name__ == '__main__':
    print("Module principal")
    logger.warning('youpi')
