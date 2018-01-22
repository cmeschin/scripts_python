#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Launch the supervisorctl for view status process
    2018-01-22 version 1: version initiale
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

# execution de la commande et récupération du retour dans une variable
actualState = subprocess.run(CMD, shell=True, stdout=subprocess.PIPE)

# analyse du fichier status
# exemple de retour pour logidoc
# nom_process                                   |Etat      |message
# beemessenger:prod_logidoc_beemessenger_esendex RUNNING    pid 12480, uptime 4:13:53
# beemessenger:prod_logidoc_beemessenger_repriserg RUNNING    pid 12474, uptime 4:13:53
# beemessenger:spool_beemessenger_batch_coriolis RUNNING    pid 12483, uptime 4:13:53
# filebeat                         STOPPED    Not started
# beemessenger:spool_beemessenger_batch_default RUNNING    pid 12472, uptime 4:13:53

#    boucle sur chaque ligne du fichier
# print("############## ligne:" + str(retour.stdout)[2:-1])
lstActualState = str(actualState.stdout)[2:-3].split("\\n")
for line in lstActualState:
    nbProcess += 1  # comptage du nombre de process configurés
    # print("ligne lue:", line)
    # découpage en trois colonnes (tabulations)
    line = ' '.join(line.split())  # supprime les espaces multiples de la chaine
    # print("ligne découpée:", line.split(" ", 2))  # on ne traite que les deux premiers espaces
    result = line.split(" ", 2)
    # si Statut différent de RUNNING, on stock les valeurs dans un tableau listError sinon dans listRunning
    if result[1] != "RUNNING":
        # print("ALERTE !!!")
        # ajout dans la variable ERROR la liste des process arrêtés
        listError += "{} {} {}\n".format(result[0], result[1], result[2])
        nbError += 1  # Comptage du nombre d'erreurs
    else:
        # print("OK")
        # ajout dans la variable RUNNING la liste des process lancés
        listRunning += "{} {} {}\n".format(result[0], result[1], result[2])
        nbOk += 1  # Comptage du nombre de process lancés
    # print("####################")

# on traite les résultats
# si des éléments sont contenus dans la liste listError, on sort un statut CRITIQUE
if nbError == nbProcess:
    # Si tous les process sont arrêtés
    status = "CRITICAL"
    message = "Tous les process sont arrêtés (" + str(nbError) + "/" + str(nbProcess) + ") à " + now + "!"
    detail = "Process KO:\n" + listError
elif nbError > 0 & nbProcess > nbError:
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
