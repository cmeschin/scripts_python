#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" check riverbed API
    - check flow sources
    - check licencing
    2020-01-24 version 1: version initiale
    2020-02-12 version 2: Ajout mode flow
    2020-02-14 version 3: correction gestion fichier pickle
    2020-02-24 version 4: Gestion des clusters
    TODO: variabiliser user/mdp
"""

import sys
import getopt
import logging
from modules import centreon_status
from modules import tessi_common

# Modules spécifiques
import os.path
import pickle
import requests

# definition des constantes
VERSION = "2020-02-24 version 4"
USERNAME = "publicring"
PASSWORD = "nd7ja*!ja"
WORK_DIR = tessi_common.define_result_folder()
STAT_FLOW = "riverbed_stat_flow.pkl"
URL_RIVERBED = "https://riverbed-gateway.interne.tessi-techno.fr/api/gateway/1.5/stats"
# CLUSTERS = {"CLUSTER1": ['10.138.101.10', '10.33.253.1'], "CLUSTER2": ['10.33.253.221', '10.33.253.222']}  # pour test
CLUSTERS = {"CLUSTER1": ['10.33.253.1', '10.33.253.2'], "CLUSTER2": ['10.33.253.221', '10.33.253.222']}

def stat_flow(exclude):
    nbErrors = 0
    # print("Mode non encore implémenté.")
    # sys.exit(0)

    # vérification de l'existence du fichier pickle
    dictIpErrors = {}
    if os.path.exists(WORK_DIR+STAT_FLOW):
        try:
            dictIpErrors = pickle.load(open(WORK_DIR+STAT_FLOW, 'rb'))
        except Exception as err:
            print("ERREUR: Impossible d'ouvrir le fichier de stat {} ({})".format(WORK_DIR+STAT_FLOW, err))
            sys.exit(3)

    # Récupération de la page
    r = requests.get(URL_RIVERBED, auth=(USERNAME, PASSWORD))

    # reformatage du résultat par ligne
    result = r.text.split("\n")  # retourne une liste de lignes
    # print(result)
    list_update = []  # crée une liste pour la mise à jour des ip
    fullline = {}  # crée un dictionnaire pour les lignes complètes avec l'ip comme clé
    # parcourir le résultat et stocker les valeurs de chaque ligne
    for line in result:
        flow = ""
        ipAddr = ""
        newLine = ""
        isCluster = False
        ipCluster = ""

        if "<flow_source flow_type" in line:
            values = line.split(" ")  # liste des valeurs de la ligne ('flow_type="SFlow"', 'flows_received_last_min="5"', 'ipaddr="10.62.101.10"', ...)

            for ips in CLUSTERS.values():
                # print("cluster: {}".format(ips))
                for ip in ips:
                    if ip in line:
                        # print("IP cluster: {}".format(ip))
                        isCluster = True
                        ipCluster = ip

            # si ce n'est pas les clusters
            if not isCluster:
            # if "10.33.253.1" not in line and "10.33.253.2" not in line and "10.33.253.221" not in line and "10.33.253.222" not in line:
                for value in values:
                    # updated = False
                    myvalue = value.split("=")
                    # print("myvalue:{}".format(myvalue))
                    # reconstruction de la ligne
                    newLine += " " + value
                    if myvalue[0] == "flows_received_last_min":
                        flow = int(value.split("=")[1].replace('"',''))
                    elif myvalue[0] == "ipaddr":
                        ipAddr = value.split("=")[1].replace('"','')
                        list_update.append(ipAddr)

                    # # print("Liste update1: {}".format(list_update))
                    # if flow != "" and ipAddr != "" and updated == True:
                    #     updated = False
                    #     #print("flow:{} {}".format(flow,ipAddr))

                # mise en forme de la chaine (suppression de la balise <flow source .../>)
                fullline[ipAddr] = newLine.strip()[13:-2]
                # Ajout de l'IP dans le dictionnaire si elle n'existe pas déjà
                if ipAddr not in dictIpErrors:
                    # print("Ajout de l'adresse {}.".format(ipAddr))
                    dictIpErrors[ipAddr] = 0

                if flow == 0 and ipAddr not in exclude:
                    # si pas de flow, on ajoute/incrémente dans le dictionnaire
                    # print("ipAddr:{}".format(ipAddr))
                    # print("exclude: {}".format(exclude))
                    nbcheck = dictIpErrors.get(ipAddr)+1
                    # print("nbcheck:{}".format(nbcheck))
                    dictIpErrors[ipAddr] = nbcheck
                    # print("ipErrors:{}".format(ipErrors[ipAddr]))
                else:
                    nbcheck = 0
                    dictIpErrors[ipAddr] = nbcheck
            else:  # c'est un cluster
                for value in values:
                    # updated = False
                    myvalue = value.split("=")
                    # print("myvalue:{}".format(myvalue))
                    # reconstruction de la ligne
                    newLine += " " + value
                    if myvalue[0] == "flows_received_last_min":
                        flow = int(value.split("=")[1].replace('"',''))
                    elif myvalue[0] == "ipaddr":
                        ipAddr = value.split("=")[1].replace('"','')
                        list_update.append(ipAddr)

                    # # print("Liste update1: {}".format(list_update))
                    # if flow != "" and ipAddr != "" and updated == True:
                    #     updated = False
                    #     #print("flow:{} {}".format(flow,ipAddr))

                    # mise en forme de la chaine (suppression de la balise <flow source .../>)
                    myCluster = ""
                    for cluster, ips in CLUSTERS.items():
                        if ipAddr in ips:
                            myCluster = cluster

                fullline[ipAddr] = "Cluster {}: {}".format(myCluster, newLine.strip()[13:-2])
                # Ajout de l'IP dans le dictionnaire si elle n'existe pas déjà
                if ipAddr not in dictIpErrors:
                    # print("Ajout de l'adresse {}.".format(ipAddr))
                    dictIpErrors[ipAddr] = 0

                if flow == 0 and ipAddr not in exclude:
                    # si pas de flow, on ajoute/incrémente dans le dictionnaire
                    nbcheck = dictIpErrors.get(ipAddr)+1
                    # print("nbcheck:{}".format(nbcheck))
                    dictIpErrors[ipAddr] = nbcheck
                    # print("ipErrors:{}".format(ipErrors[ipAddr]))
                    # Récupération IP secondaire
                    for cluster, ips in CLUSTERS.items():
                        if ipAddr in ips and ipAddr != ips[0]:
                            ipAddr2 = ips[0]
                        else:
                            ipAddr2 = ips[1]

                    for line in result:
                        if ipAddr2 in line:
                            myLine = result.index(line)  # recupère l'index de la ligne contenant l'ipAddr2
                            values = result[myLine].split(" ")

                    for value in values:
                        # updated = False
                        myvalue = value.split("=")
                        # print("myvalue:{}".format(myvalue))
                        # reconstruction de la ligne
                        newLine += " " + value
                        if myvalue[0] == "flows_received_last_min":
                            flow = int(value.split("=")[1].replace('"',''))
                        elif myvalue[0] == "ipaddr":
                            ipAddr = value.split("=")[1].replace('"','')
                            list_update.append(ipAddr)

                    # # print("Liste update1: {}".format(list_update))
                    # if flow != "" and ipAddr != "" and updated == True:
                    #     updated = False
                    #     #print("flow:{} {}".format(flow,ipAddr))

                    # mise en forme de la chaine (suppression de la balise <flow source .../>)
                    fullline[ipAddr] = newLine.strip()[13:-2]
                    # Ajout de l'IP dans le dictionnaire si elle n'existe pas déjà
                    if ipAddr not in dictIpErrors:
                        # print("Ajout de l'adresse {}.".format(ipAddr))
                        dictIpErrors[ipAddr] = 0

                    if flow == 0 and ipAddr not in exclude:
                        # si pas de flow, on ajoute/incrémente dans le dictionnaire
                        # print("ipAddr:{}".format(ipAddr))
                        # print("exclude: {}".format(exclude))
                        nbcheck = dictIpErrors.get(ipAddr)+1
                        # print("nbcheck:{}".format(nbcheck))
                        dictIpErrors[ipAddr] = nbcheck
                        # print("ipErrors:{}".format(ipErrors[ipAddr]))
                    else:
                        nbcheck = 0
                        dictIpErrors[ipAddr] = nbcheck


                else:
                    nbcheck = 0  # reinit du compteur
                    dictIpErrors[ipAddr] = nbcheck

    # Nettoyage du dictionnaire des ip qui n'existe plus
    del_ip = []
    # print("Liste update: {}".format(list_update))
    for ip in dictIpErrors.keys():
        if ip not in list_update:
            # print("IP: {}".format(ip))
            del_ip = list.append("{}".format(ip))
            # print("Suppression de l'ip {}".format(ip))

    # Mise à jour du dictionnaire
    for ip in del_ip:
        del dictIpErrors[ip]
        # print("Suppression de l'IP {} dans le dictionnaire.".format(ip))

    # sauvegarde du résultat dans le fichier pickle
    try:
        pickle.dump(dictIpErrors, open(WORK_DIR+STAT_FLOW, 'wb'))
    except IOError as err:
        print("ERREUR: Impossible d'ecrire le fichier stat {} ({}).".format(WORK_DIR+STAT_FLOW, err))
        sys.exit(3)

    # analyse du résultat
    # si une ou plusieurs IP sont à trois check ou plus on remonte l'alerte
    ipErrors = {}

    for ip, nbErr in dictIpErrors.items():
        isCluster = False
        indexCluster = ""
        # print("Cle: {}, Valeur: {}, ipErrors: {}".format(cle, valeur,ipErrors))
        for cluster, ips in CLUSTERS.items():
            if ip in ips:
                isCluster = True
                indexCluster = cluster

        if not isCluster and nbErr >= 3:  # pas cluster et erreurs
            # print("Cle {}".format(cle))
            ipErrors[ip] = fullline[ip]
            nbErrors = nbErrors+1  # nombre de ligne en erreur
            # print("Ajout Error: {}".format(ipErrors[ip]))
        elif isCluster:  # cluster
            myClusterErr = False
            for ips in CLUSTERS[indexCluster]:
                # print("Value IndexCLuster {}: {}".format(indexCluster, ips))
                if dictIpErrors[ips] >= 3:
                    myClusterErr = True
                    ipErrors[ips] = fullline[ips]
                else:
                    myClusterErr = False
            if myClusterErr == True:
                nbErrors = nbErrors+1

    if nbErrors >= 1:
        status = "CRITICAL"
        message = "Le flow de {} équipement(s) est nul.".format(nbErrors)
        detail = "Liste des équipements concernés:\n"
        for cle,valeur in ipErrors.items():
            detail += "{}: {}\n".format(cle, valeur)
        perfdata = ""
    else:
        status = "OK"
        message = "Tous les équipements remontent des données."
        detail = ""
        perfdata = ""
    centreon_status.exit(status, message, detail, perfdata)


def stat_licencing(warning, critical):

    WARN = warning
    CRIT = critical
    # Récupération de la page
    r = requests.get(URL_RIVERBED, auth=(USERNAME, PASSWORD))

    # reformatage du résultat par ligne
    result = r.text.split("\n")

    # parcourir le résultat et stocker les valeurs de chaque ligne
    for line in result:
        if "<stats" in line:
            # print(line)
            # recupérer capacity et flows_received_last_min
            values = line.split(" ")
            # get capacity
            for value in values:
                myvalue = value.split("=")
                # print("## myvalue: "+myvalue[0])
                if myvalue[0] == "capacity":
                    # print(value)
                    capacity=int(value.split("=")[1].replace('"',''))
                    # print("##### mycapacity="+str(capacity))
                elif myvalue[0] == "flows_received_last_min":
                    # print(value)
                    flow=int(value.split("=")[1].replace('"',''))
                    # print("##### myFlow="+str(flow))

    # print("Capacity:"+str(capacity)+"; Flow:"+str(flow))
    prct_flow = round(flow*100/capacity,2)
    warn_flow = round(WARN*capacity/100)
    crit_flow = round(CRIT*capacity/100)
    # print(str(prct_flow) +"%")
    if prct_flow >= CRIT:
        status = "CRITICAL"
        message = "Le flux reçu sur la dernière minute ({} soit {}%) est supérieur à {}% de la capacité totale de la licence ({}).".format(flow, prct_flow, CRIT, capacity)
        detail = ""
        perfdata = "flow={};{};{};0;{}".format(flow, warn_flow, crit_flow, capacity)
    elif prct_flow >= WARN:
        status = "WARNING"
        message = "Le flux reçu sur la dernière minute ({} soit {}%) est supérieur à {}% de la capacité totale de la licence ({}).".format(flow, prct_flow, WARN, capacity)
        detail = ""
        perfdata = "flow={};{};{};0;{}".format(flow, warn_flow, crit_flow, capacity)
    else:
        status = "OK"
        message = "Le flux reçu sur la dernière minute ({} soit {}%) est inférieur à {}% de la capacité totale de la licence ({}).".format(flow, prct_flow, WARN, capacity)
        detail = ""
        perfdata = "flow={};{};{};0;{}".format(flow, warn_flow, crit_flow, capacity)
    centreon_status.exit(status, message, detail, perfdata)


def main(argv):
    mode = ''
    warning = 'NC'
    critical = 'NC'
    exclude = ""

    # création du répertoire de travail
    tessi_common.create_result_folder()

    try:
        opts, args = getopt.getopt(argv, "hm:w:c:v:e",["help", "version", "mode=", "warning=", "critical=", "exclude="])
    except getopt.GetoptError:
        print("INCONNU: Cas non géré: {} -m <mode> -w <warning> -c <critical>".format(sys.argv[0]))
        sys.exit(3)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("{} -m <mode: licencing ou flow> -w <licencing warning capacity (%)> -c <licencing critical capacity (%)> -e <exclusion d'adresses>".format(sys.argv[0]))
            sys.exit(0)
        elif opt in ("-v", "--version"):
            print("Script {} {}".format(sys.argv[0], VERSION))
            sys.exit(0)
        elif opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-w", "--warning"):
            warning = arg
        elif opt in ("-c", "--critical"):
            critical = arg
        elif opt in ("-e", "--exclude"):
            exclude = arg

    if mode == "licencing":
        try:
            warning = int(warning)
            critical = int(critical)
        except ValueError:
            print("ERREUR: les seuils warning ({}) et critical ({}) doivent être des nombres".format(warning,critical))
            sys.exit(3)

        if (warning > 100 or warning < 0) or (critical > 100 or critical < 0):
            print("ERREUR: Les seuils warning ({}) et critical ({}) doivent être compris entre 0 et 100.".format(warning, critical))
            sys.exit(3)
        elif warning >= critical:
            print("ERREUR: le seuil warning ({}) doit être inférieur au seuil critical ({}).".format(warning, critical))
            sys.exit(3)
        stat_licencing(warning,critical)
    elif mode == "flow":
        if exclude != "":
            try:
                exclude = str(exclude).split(",")
            except Exception:
                print("ERREUR: la valeur {} n'est pas valide.".format(exclude))
                sys.exit(3)
        stat_flow(exclude)
    else:
        print("ERREUR: mode {} inconnu. Modes attendus: licencing ou flow uniquement.".format(mode))
        print("Script {} {}".format(sys.argv[0], VERSION))
        sys.exit(3)


if __name__ == "__main__":
    main(sys.argv[1:])
