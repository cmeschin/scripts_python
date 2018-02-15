#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Launch the supervisorctl for view status process
    2018-01-22 version 1: version initiale
    2018-02-08 version 2: gestion python2 et python3
    2018-02-15 version 3: correction opérateur logique & en and
"""

# import des modules
import subprocess

from modules import centreon_status
from modules import tessi_common

# definition des constantes "globales"
CMD = "sudo /usr/bin/supervisorctl status"

# definition des variables "globales"
detail = ""
listError = ""
listRunning = ""
nbError = 0
nbOk = 0
nbProcess = 0
now = tessi_common.define_now()


# analyse du fichier status
# exemple de retour pour logidoc
# nom_process                                   |Etat      |message
# beemessenger:prod_logidoc_beemessenger_esendex RUNNING    pid 12480, uptime 4:13:53
# filebeat                         STOPPED    Not started

#récupération de la version de python
version = tessi_common.get_version_python()

# execution de la commande selon la version de python et récupération du retour dans une variable
if version[:1] == "2":
    actualState = subprocess.check_output(CMD, shell=True)

    lstActualState = str(actualState)[:-3].split('\n')
elif version[:1] == "3":
    actualState = subprocess.run(CMD, shell=True, stdout=subprocess.PIPE)

    lstActualState = str(actualState.stdout)[2:-3].split("\\n")

for line in lstActualState:
    nbProcess += 1  # comptage du nombre de process configurés
    # découpage en trois colonnes (tabulations)
    line = ' '.join(line.split())  # supprime les espaces multiples de la chaine
    result = line.split(" ", 2)
    # si Statut différent de RUNNING, on stock les valeurs dans un tableau listError sinon dans listRunning
    if result[1] != "RUNNING":
        # ajout dans la variable ERROR la liste des process arrêtés
        listError += "{} {} {}\n".format(result[0], result[1], result[2])
        nbError += 1  # Comptage du nombre d'erreurs
    else:
        # ajout dans la variable RUNNING la liste des process lancés
        listRunning += "{} {} {}\n".format(result[0], result[1], result[2])
        nbOk += 1  # Comptage du nombre de process lancés

# on traite les résultats
# si des éléments sont contenus dans la liste listError, on sort un statut CRITIQUE
if nbError == nbProcess:
    # Si tous les process sont arrêtés
    status = "CRITICAL"
    message = "Tous les process sont arrêtés (" + str(nbError) + "/" + str(nbProcess) + ") à " + now + "!"
    detail = "Process KO:\n" + listError
elif nbError > 0 and nbProcess > nbError:
    # s'il y a des erreurs mais en nombre inférieur au nombre total de process => WARNING
    status = "WARNING"
    message = str(nbError) + " process sur " + str(nbProcess) + " arrêté(s) à " + now + "!"
    detail = "Process KO:\n" + listError + "Process OK:\n" + listRunning
elif nbOk == nbProcess:
    status = "OK"
    message = "Tous les process sont démarrés (" + str(nbOk) + "/" + str(nbProcess) + ") à " + now + "."
    detail = "Process OK:\n" + listRunning
else:
    status = "UNKNOWN"
    message = "Cas non géré: nbProcess=" + str(nbProcess) + "; nbError=" + str(nbError) + "; nbOK=" + str(nbOk) + \
              " a " + now + ". Contacter l'équipe centreon (centreon_tt@tessi.fr) pour analyse. "

centreon_status.exit(status, message, detail)
