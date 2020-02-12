#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import subprocess
import sys
import time

"""
    Module de gestion des classes et méthodes communes aux script tessi
    date, répertoire de résultats, etc...
    consulter http://strftime.org/ pour les format possibles
"""
"""
    2018-02-08 version 1: version initiale
        - définition des fonctions basiques
"""


def define_result_folder():
    """Méthode de définition du répertoire de stockage des résultats et fichiers temporaires
        selon la plateforme (Windows ou Linux)
    """
    if sys.platform == "win32":
        return "C:/supervision/scripts/resultats/"
    else:
        return "/supervision/resultats/"


def define_now(format="%Hh%M"):
    """ Méthode permettant de retourner une chaine de l'heure actuelle en fonction du format indiqué
        :param format: format de l'heure attendue (par défaut %Hh%M)
    """
    now = time.strftime(format, time.localtime())
    return now


def define_today(format="%d/%m/%Y"):
    """ Méthode permettant de retourner une chaine de la date actuelle en fonction du format indiqué
        :param format: format de l'heure attendue (par défaut %d/%m/%Y)
    """
    today = datetime.datetime.now().strftime(format)
    return today


def define_day(format="%A"):
    """ Méthode permettant de retourner une chaine du jour de la semaine en fonction du format indiqué
        :param format: format de l'heure attendue (par défaut %A => like Monday)
    """
    dayofweek = datetime.datetime.now().strftime(format)
    return dayofweek


def define_month(format="%B"):
    """ Méthode permettant de retourner une chaine du mois en cours en fonction du format indiqué
        :param format: format de l'heure attendue (par défaut %B => like September)
    """
    month = datetime.datetime.now().strftime(format)
    return month


def define_year(format="%Y"):
    """ Méthode permettant de retourner une chaine de l'année en cours en fonction du format indiqué
            :param format: format de l'heure attendue (par défaut %Y => like 2018)
    """
    year = datetime.datetime.now().strftime(format)
    return year


def get_bin_python():
    """ Méthode permettant de récupérer le chemin du binaire python
    """
    bin_python = sys.executable
    return bin_python


def get_version_python():
    """ Méthode permettant de récupérer la version du binaire python
    """
    version_python = sys.version.split(" ", 1)[0]
    return version_python

def exec_command(cmd):
    #récupération de la version de python
    version = get_version_python()

    # execution de la commande selon la version de python et récupération du retour dans une variable
    if version[:1] == "2":
        result_cmd = subprocess.check_output(cmd, shell=True)
    elif version[:1] == "3":
        result_cmd = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    return result_cmd

if __name__ == "__main__":
    print("-- Module de gestion des classes et méthodes communes aux scripts tessi (format de date, "
          "répertoire de résultats, etc... --")
    print(sys.argv[1:])
