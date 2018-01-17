#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Launch the supervisorctl for view status process
"""

import os, subprocess

cmd = "sudo supervisorctl status"
path = "/supervision/resultats/" # prévoir l'utilisation du chemin relatif pour une compatibilité avec les chemin Windows
supervisorctl = "status_process_supervisorctl.txt"
status_supervisorctl = (path + supervisorctl)

#List the file in directory for delete file_status
#TODO: Si le fichier xxxx.txt est dans le dossier /supervision/resultats/  alors le supprimer sinon lancer la commande.
for root, dirs, files in os.walk(path):
    for filename in files:
        print(filename)

os.remove(status_supervisorctl)

#Launch the new file_status
subprocess.run(cmd= $cmd, output= $path_$status_supervisorctl)

#analyse du fichier status
# exemple de retour pour logidoc
# nom_process                                  |Etat      |message
#beemessenger:prod_logidoc_beemessenger_esendex RUNNING    pid 12480, uptime 4:13:53
#beemessenger:prod_logidoc_beemessenger_repriserg RUNNING    pid 12474, uptime 4:13:53
#beemessenger:spool_beemessenger_batch_coriolis RUNNING    pid 12483, uptime 4:13:53
#beemessenger:spool_beemessenger_batch_default RUNNING    pid 12472, uptime 4:13:53

# boucle sur chaque ligne du fichier
# découpage en trois colonnes (tabulations)
# si Statut différent de RUNNING, on stocke les valeurs dans un tableau ERROR sinon dans un tab