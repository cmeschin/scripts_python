#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Launch the supervisorctl for view status process
"""

import os, subprocess, time

# definition des constantes
from modules import centreon_status

maintenant = time.strftime("%Hh%M", time.gmtime())

#cmd = "sudo supervisorctl status"
#cmd = "type d:\python\scripts_python\log\status.txt"
cmd = "cmd /c type d:\python\scripts_python\log\status.txt"
#path = "/supervision/resultats/"
# TODO: prévoir l'utilisation du chemin relatif pour une compatibilité avec les chemins Windows

supervisorctl = "supervisorctl_status.txt"
status_supervisorctl = (path + supervisorctl)

# List the file in directory for delete file_status and Launch for new file_status
# TODO: Commande suppression OK ==>A tester lancer la commande.
from pathlib import Path

# if os.path.exists(status_supervisorctl):
#     os.remove(status_supervisorctl)
# # Tester la commande.
# else:
    #subprocess.run(cmd= $cmd, output= $path_$status_supervisorctl)
retour = subprocess.run(cmd, stdout=subprocess.PIPE)
#print("retour=" + str(retour.stdout))

# analyse du fichier status
# exemple de retour pour logidoc
# nom_process                                  |Etat      |message
# beemessenger:prod_logidoc_beemessenger_esendex RUNNING    pid 12480, uptime 4:13:53
# beemessenger:prod_logidoc_beemessenger_repriserg RUNNING    pid 12474, uptime 4:13:53
# beemessenger:spool_beemessenger_batch_coriolis RUNNING    pid 12483, uptime 4:13:53
# filebeat                         STOPPED    Not started
# beemessenger:spool_beemessenger_batch_default RUNNING    pid 12472, uptime 4:13:53

# ouvrir le fichier
#with open("D:/Python/scripts_python/log/status.txt", "r") as file:
    # boucle sur chaque ligne du fichier
nbProcess = 0
nbError = 0
nbOk = 0
list_running = ""
list_error = ""
detail = ""
#print("############## ligne:" + str(retour.stdout)[2:-1])
retour=str(retour.stdout)[2:-1].split("\\r\\n")
for ligne in retour:
    nbProcess += 1  # comptage du nombre de process configurés
    print("ligne lue:", ligne)
    # découpage en trois colonnes (tabulations)
    ligne = ' '.join(ligne.split())  # supprime les espaces multiples de la chaine
    print("ligne découpée:", ligne.split(" ", 2))  # on ne traite que les deux premiers espaces
    result = ligne.split(" ", 2)
    # si Statut différent de RUNNING, on stock les valeurs dans un tableau list_error sinon dans list_running
    if result[1] != "RUNNING":
        print("ALERTE !!!")
        # ajout dans la variable ERROR la liste des process arrêtés
        list_error += "{} {} {}\n".format(result[0],result[1],result[2])
        nbError += 1  # Comptage du nombre d'erreurs
    else:
        print("OK")
        # ajout dans la variable RUNNING la liste des process lancés
        list_running += "{} {} {}\n".format(result[0],result[1],result[2])
        nbOk += 1  # Comptage du nombre de process lancés
    print("####################")

# on traite les résultats
# si des éléments sont contenus dans la liste list_error, on sort un statut CRITIQUE
if nbError == nbProcess:
    # Si tous les process sont arrêtés
    status = "CRITICAL"
    message = "Tous les process sont arrêtés (" + str(nbError) + "/" + str(nbProcess) + ") à " + maintenant + "!"
    detail = "Process KO:\n" + list_error
elif not nbError <= 0 & nbProcess > nbError:
    # s'il y a des erreurs mais en nombre inférieur au nombre total de process => WARNING
    status = "WARNING"
    message = str(nbError) + " process sur " + str(nbProcess) + " arrêté(s) à " + maintenant + "!"
    detail = "Process KO:\n" + list_error + "Process OK:\n" + list_running
elif nbOk == nbProcess:
    status = "OK"
    message = "Tous les process sont démarrés (" + str(nbOk) + "/" + str(nbProcess) + ") à " + maintenant + "."
    detail = "Process OK:\n" + list_running
else:
    status = "UNKNOWN"
    message = "Cas non géré: nbProcess=" + str(nbProcess) + "; nbError=" + str(nbError) + "; nbOK=" + str(nbOk) + \
    " a " + maintenant + ". Contacter l'équipe centreon (centreon_tt@tessi.fr) pour analyse. "

centreon_status.exit(status, message, detail)
