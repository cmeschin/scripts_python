#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Launch the supervisorctl for view status process
"""

import os, subprocess

cmd = "sudo supervisorctl status"
path = "/supervision/resultats/"
#TODO: prévoir l'utilisation du chemin relatif pour une compatibilité avec les chemin Windows

supervisorctl = "supervisorctl_status.txt"
status_supervisorctl = (path + supervisorctl)

#List the file in directory for delete file_status
#TODO: Si le fichier xxxx.txt est dans le dossier /supervision/resultats/  alors le supprimer sinon lancer la commande.
#  for root, dirs, files in os.walk(path):
#      for filename in files:
#          print(filename)
#
# os.remove(status_supervisorctl)

#Launch the new file_status
#subprocess.run(cmd= $cmd, output= $path_$status_supervisorctl)

#analyse du fichier status
# exemple de retour pour logidoc
# nom_process                                  |Etat      |message
#beemessenger:prod_logidoc_beemessenger_esendex RUNNING    pid 12480, uptime 4:13:53
#beemessenger:prod_logidoc_beemessenger_repriserg RUNNING    pid 12474, uptime 4:13:53
#beemessenger:spool_beemessenger_batch_coriolis RUNNING    pid 12483, uptime 4:13:53
#filebeat                         STOPPED    Not started
#beemessenger:spool_beemessenger_batch_default RUNNING    pid 12472, uptime 4:13:53

# ouvrir le fichier
with open("C:/supervision/Scripts/resultats/supervisorctl_status.txt", "r") as file:
    # boucle sur chaque ligne du fichier
    for line in file:
        ligne=line
        #print("ligne lue:", ligne)
        # découpage en trois colonnes (tabulations)
        ligne=' '.join(ligne.split())  # supprime les espaces multiples de la chaine
        print("ligne découpée:", ligne.split(" ", 2))  # on ne traite que les deux premiers espaces
        result = ligne.split(" ", 2)
        if result[1] != "RUNNING":
            print("ALERTE !!!")
            # ajout dans la variable ERROR la liste des process arrêtés
            # blabla
        print("####################")

# si Statut différent de RUNNING, on stocke les valeurs dans un tableau ERROR sinon dans un tab