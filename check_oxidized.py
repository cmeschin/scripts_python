#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Check sauvegardes Oxidized
    Parcours d'une ressource web (format JSON) pour remonter les sauvegardes en erreur.
    - remonte une alerte si "supervision"="oui" et "status" = "no_connection"
    - liste les objets à "supervision" = "non" pour suivi

    2020-03-17 version 1: version initiale
"""
import sys
import getopt
import logging
from modules import centreon_status
from modules import tessi_common

# Modules spécifiques
import json
import requests


# definition des constantes
VERSION = "2020-03-17 version 1"
URL = "https://oxidized.interne.tessi-techno.fr/nodes.json"

def get_stats(url):
    """
    Get stats from JSON
    :return:
        statsResult: Json dictionnary
    """
    statsResult = []
    r = requests.get(url)  # récupération de la page
    statsResult = json.loads(r.text)  # formattage en json sous forme de list

    return statsResult


def main(argv):
    # création du répertoire de travail
    tessi_common.create_result_folder()

    try:
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.GetoptError:
        print("INCONNU: Cas non géré: {} --help".format(sys.argv[0]))
        sys.exit(3)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("{} --help".format(sys.argv[0]))
            print("Affiche cette aide.")
            print("Ce script ne requiert aucun argument.")
            sys.exit(0)

    dictListSwitch = {}
    dictListExclu = {}

    statsResult = get_stats(URL)
    for obj in statsResult:
        if obj["supervision"] == "oui" and obj["last"]["status"] == "no_connection":
            dictListSwitch[obj["name"]] = str(obj["name"]) + " " + str(obj["ip"]) + ": dernier statut " + str([obj["last"]["status"]]) + " le " + str(obj["last"]["end"]) + "."
        elif obj["supervision"] == "non":
            dictListExclu[obj["name"]] = obj["name"] + " " + obj["ip"]

    detailSwitch = "Liste des switch exclus:\n"
    for nom, obj in dictListExclu.items():
        detailSwitch += "{}\n".format(obj)

    if dictListSwitch:
        status = "CRITICAL"
        message = "La sauvegarde de {} équipement(s) n'a pu être effectuée correctement.".format(len(dictListSwitch))
        detail = "Liste des équipements concernés:\n"
        for value in dictListSwitch.values():
            detail += "{}\n".format(value)
        detail += detailSwitch
        perfdata = ""
    else:
        status = "OK"
        message = "La sauvegarde de tous les équipements est à jour."
        detail = detailSwitch
        perfdata = ""
    centreon_status.exit(status, message, detail, perfdata)


if __name__ == "__main__":
    main(sys.argv[1:])


