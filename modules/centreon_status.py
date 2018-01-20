#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

"""
    Module de gestion des statuts de sortie pour centreon
    :param STATUT : Statut de la sonde (obligatoire)
    :param MESSAGE : statut détaillé (première ligne) (obligatoire)
    :param DETAIL : statut détaillé étendu (à partir de la seconde ligne) (optional)
    :param PERFDATA : données de performance pour les graphes (optional)
    :return: Retourne à centreon les détails de l'exécution du script

    :example:
    Statuts CENTREON:
        OK => 0
        WARNING => 1
        CRITICAL => 2
        UNKNOWN => 3
    Format des messages de sortie:
        - le première ligne indique le statut détaillé avec le l'état
        - la seconde ligne (optionnelle) indique le statut détaillé étendu
        - la troisième ligne (optionnelle) renvoie les données de performance (précédées d'un pipe "|")

        <STATUT>: Message de sortie principal
        message détaillé
        | données de performance
"""


def define_state(status):
    """Fonction de définition du code de sortie en fonction du statut"""
    if status == "OK":
        exit_code = 0
        exit_status = "OK"
    elif status == "WARNING":
        exit_code = 1
        exit_status = "ATTENTION"
    elif status == "CRITICAL":
        exit_code = 2
        exit_status = "CRITIQUE"
    elif status == "UNKNOWN":
        exit_code = 3
        exit_status = "INCONNU"
    else:
        print("INCONNU: Statut [" + status + "] non géré.")
        print("Statuts attendus: OK WARNING CRITICAL UNKNOWN")
        sys.exit(3)
    sortie = (exit_status, exit_code)
    return sortie


def exit(status, message, detail="", perfdata=""):
    """ Fonction de renvoie du message à centreon"""
    exit_return = define_state(status)
    print(exit_return[0] + ': ' + message)
    if detail != "":
        print(detail)
    if perfdata != "":
        print(perfdata)
    sys.exit(exit_return[1])


if __name__ == "__main__":
    print("-- fonction de retour des états des scripts pour centreon --")
    print(sys.argv[1:])
