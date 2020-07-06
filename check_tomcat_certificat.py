#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Check certificat
    Contrôle l'état d'un certficat via l'outil keytool

    2020-06-29 version 1: version initiale
    2020-07-03 version 2: ajout de l'alias dans le message de retour
    2020-07-06 version 3: Correction gestion stdout (intégration dans tessi_common)
                        Prise en compte des arguments facultatifs vides
"""
import sys
import getopt
from modules import centreon_status
from modules import tessi_common

# Modules spécifiques
from datetime import datetime


# definition des constantes
VERSION = "2020-07-06 version 3"


def expiration(alias, password, warning, critical, keystore, keytool):
    """
    Get certificat expiration date
    :return:
        exit code, messages and perfdata for centreon
    """
    # Affectation de constantes
    today = datetime.now()
    # today = datetime.now() + timedelta(days=280)
    # print(today)
    CMD = keytool + " -list -v -alias \"" + alias + "\" -keystore " + keystore + " -storepass " + password
    tessi_common.exec_command(CMD)
    result_cmd, result_cmd_stdout = tessi_common.exec_command(CMD)
    # conversion du retour stdout en liste
    lstResult = result_cmd_stdout.split("\\n")
    for element in lstResult:
        # print(element)
        # exemple: Valid from: Wed Apr 29 11:24:01 CEST 2020 until: Thu Apr 29 11:24:01 CEST 2021
        if "Valid from" in element:
            myDate = element.split("until: ", 1)[1]
            # print("######" + expirationDate)
            expirationDate = datetime.strptime(myDate, '%a %b %d %H:%M:%S CEST %Y')
            diff = expirationDate - today
            if diff.days <= 0:
                status = "CRITICAL"
                message = "Le certificat [{}] est expiré depuis {} jour(s). Date expiration: {}".format(alias,
                                                                                                        abs(diff.days),
                                                                                                        expirationDate)
                detail = ""
                perfdata = ""
            elif diff.days <= critical and diff.days != 0:
                status = "CRITICAL"
                message = "Le certificat [{}] expire dans {} jours.Date expiration: {}".format(alias, diff.days,
                                                                                               expirationDate)
                detail = ""
                perfdata = ""
            elif diff.days <= warning:
                status = "WARNING"
                message = "Le certificat [{}] expire dans {} jours. Date expiration: {}".format(alias, diff.days,
                                                                                                expirationDate)
                detail = ""
                perfdata = ""
            elif diff.days > warning:
                status = "OK"
                message = "Le certificat [{}] expire dans {} jours. Date expiration: {}".format(alias, diff.days,
                                                                                                expirationDate)
                detail = ""
                perfdata = ""
            else:
                status = "UNKNOWN"
                message = "Cas non géré - Certificat: {} - Keystore: {} - Keytool: {} - Date expiration: {} - " \
                          "Warning: {} - Critical: {} - Différentiel de date: {}.".format(alias, keystore, keytool,
                                                                                          expirationDate, warning,
                                                                                          critical, diff.days)
                detail = ""
                perfdata = ""
            centreon_status.exit(status, message, detail, perfdata)


def main(argv):
    mode = ''
    alias = ''
    password = 'changeit'
    warning = '30'
    critical = '10'
    keystore = "D:/Docubase/server/jre/lib/security/jssecacerts"
    keytool = "D:/Docubase/server/jre/bin/keytool.exe"

    # création du répertoire de travail
    tessi_common.create_result_folder()

    try:
        opts, args = getopt.getopt(argv, "hmap:w:c:k:K:v", ["help", "mode=", "alias=", "password=", "warning=",
                                                            "critical=", "keystore", "keytool", "version"])
    except getopt.GetoptError:
        print("INCONNU: Cas non géré: {} -m <mode> -w <warning> -c <critical>".format(sys.argv[0]))
        sys.exit(3)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            helpMessage = """
            {}
            -m --mode: expiration - Check certificat expiration date - Mandatory
            -a --alias: certificat alias name - Mandatory
            -p --password: keystore password - Mandatory
            -w --warning: Number of days for warning alert (default: 30 days) - Optionnal
            -c --critical: Number of days for critical alert (default: 0 days, expired) - Optionnal
            -k --keystore: fullname keytore path (default: D:/Docubase/server/jre/lib/security/jssecacerts) - Optionnal
            -K --keytool: fullname keytool path (default:  D:/Docubase/server/jre/bin/keytool) - Optionnal
            """
            print(helpMessage.format(sys.argv[0]))
            sys.exit(0)
        elif opt in ("-v", "--version"):
            print("Script {} {}".format(sys.argv[0], VERSION))
            sys.exit(0)
        elif opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-a", "--alias"):
            alias = arg
        elif opt in ("-p", "--password"):
            if arg != "":
                password = arg
        elif opt in ("-w", "--warning"):
            if arg != "":
                warning = arg
        elif opt in ("-c", "--critical"):
            if arg != "":
                critical = arg
        elif opt in ("-k", "--keystore"):
            if arg != "":
                keystore = arg
        elif opt in ("-K", "--keytool"):
            if arg != "":
                keytool = arg

    if mode == "expiration":
        try:
            warning = int(warning)
            critical = int(critical)
        except ValueError:
            print("ERREUR: les seuils warning ({}) et critical ({}) doivent être des nombres entier".format(warning,
                                                                                                            critical))
            sys.exit(3)

        if (warning < 0) or (critical < 0):
            print("ERREUR: Les seuils warning ({}) et critical ({}) doivent être positifs.".format(warning, critical))
            sys.exit(3)
        elif warning <= critical:
            print("ERREUR: le seuil warning ({}) doit être supérieur au seuil critical ({}).".format(warning, critical))
            sys.exit(3)
        expiration(alias, password, warning, critical, keystore, keytool)
    else:
        print("ERREUR: mode {} inconnu. Modes attendus: expiration uniquement.".format(mode))
        print("Script {} {}\n{} --help pour afficher l'aide".format(sys.argv[0], VERSION, sys.argv[0]))
        sys.exit(3)


if __name__ == "__main__":
    main(sys.argv[1:])
