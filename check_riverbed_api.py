#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" check riverbed API
    - check flow sources
    - check licencing
    2020-01-24 version 1: version initiale
    2020-02-12 version 2: Ajout mode flow
    2020-02-14 version 3: correction gestion fichier pickle
    2020-02-24 version 4: Gestion des clusters
    2020-03-04 version 5: correction sur la gestion des clusters
                            refonte du script
    2020-03-05 version 6: Ajout des clusters configurés dans le message de sortie
                            Ajout de la liste des ips exclues dans le message de sortie
    TODO: variabiliser user/mdp
"""

import sys
import getopt
# import logging
from modules import centreon_status
from modules import tessi_common

# Modules spécifiques
import os.path
import pickle
import requests

# definition des constantes
VERSION = "2020-03-05 version 6"
USERNAME = "publicring"
PASSWORD = "nd7ja*!ja"
WORK_DIR = tessi_common.define_result_folder()
STAT_FLOW = "riverbed_stat_flow.pkl"
URL_RIVERBED = "https://riverbed-gateway.interne.tessi-techno.fr/api/gateway/1.5/stats"
# CLUSTERS = {"CLUSTER1": ['10.138.101.10', '10.33.253.1'], "CLUSTER2": ['10.33.253.221', '10.33.253.222']}  # pour test
CLUSTERS = {"CLUSTER1": ['10.33.253.1', '10.33.253.2'], "CLUSTER2": ['10.33.253.221', '10.33.253.222']}


def get_existing_errors(my_dict, ipaddr):
    """
    Function to get nbErrors saved on last check
    :return:
    """
    try:
        nbErrors = my_dict[ipaddr][2]
        # print("my_dict: {} {}".format(nbErrors, my_dict[ip_addr]))
    except KeyError:
        nbErrors = 0
    # print("nbErrors: {}".format(nbErrors))
    return nbErrors


def get_ip_from_cluster(name):
    """
    Function to return the two IPs of a cluster
    :param name:
    :return ip1, ip2:
    """
    ip1 = CLUSTERS[name][0]
    ip2 = CLUSTERS[name][1]

    return ip1, ip2


def get_is_cluster(ip_addr):
    """
    Function to determine if ipAddr is a cluster
    :return:
        isCluster: boolean
        nomCluster: varchar
    """
    isCluster = False
    nomCluster = ""
    for nom, ips in CLUSTERS.items():
        # print("cluster: {}".format(ips))
        if ip_addr in ips:
            # print("IP cluster: {}".format(ip))
            isCluster = True
            nomCluster = nom
            break  # si c'est un cluster on sort de la boucle

    # print("isCluster: {} {} {}".format(ipAddr, nomCluster, isCluster))
    return isCluster, nomCluster


def get_is_exclude(exclude, ip_addr):
    """
    Function to determine if ipAddr is exclude
    :return:
        isExclude: boolean
    """
    isExclude = False
    if ip_addr in exclude:
        isExclude = True
    return isExclude


def get_ip_addr(value):
    """
    Function to extract ip_addr in line
    :return:
        ip_addr: ip address
    """
    ip_addr = value.split("=")[1].replace('"', '')
    # print("ip_addr={}".format(ip_addr))
    return ip_addr


def get_stats(url, username, password):
    """
    Get stats over API
    :return:
        statsResult: list of each lines filtered with <stats, <profiler and <flow_source values
    """
    statsResult = []
    r = requests.get(url, auth=(username, password))
    tmpStat = r.text.split("\n")
    for line in tmpStat:
        if "<stats " in line or "<profiler " in line or "<flow_source " in line:
            statsResult.append(line)
    return statsResult


def get_stats_flow():
    """
    Format statsResult to only stats of flow_source
    :return:
        statsFlow: list of flow_source
    """

    statsResult = get_stats(URL_RIVERBED, USERNAME, PASSWORD)
    statsFlow = []
    for line in statsResult:
        if "<flow_source" in line:  # si la ligne contient
            newLine = line.strip()[13:-2]
            statsFlow.append(newLine)
    return statsFlow


def get_values(line):
    """
    Return all values of line
    example:
        ['isExclude',   'nomCLuster',   'nbErrors', 'line'                                               ]
        ['False',       'none',         '0',        'flow_type="SFlow" flows_received_last_min="15"
         ip_addr="10.62.101.10" last_min="1582726323" name="N/A" status="N/A" timeslice_violation="false"
          versions="5"'   ]
    :return:
        isExclude
        nomCluster
        nbErrors
        flow
    """
    flow = ""
    isExclude = line[0]
    nomCluster = line[1]
    nbErrors = line[2]
    myValues = line[3].split(" ")
    # myValues = myValues.split("=")
    for value in myValues:
        myValue = value.split("=")
        if myValue[0] == "flows_received_last_min":
            flow = int(myValue[1].replace('"', ''))

    return isExclude, nomCluster, nbErrors, flow


def stat_flow(exclude):
    # nbErrors = 0
    # print("Mode non encore implémenté.")
    # sys.exit(0)

    # vérification de l'existence du fichier pickle et chargement s'il existe
    dictListIP = {}
    if os.path.exists(WORK_DIR+STAT_FLOW):
        try:
            dictListIP = pickle.load(open(WORK_DIR+STAT_FLOW, 'rb'))
        except Exception as err:
            print("ERREUR: Impossible d'ouvrir le fichier de stat {} ({})".format(WORK_DIR+STAT_FLOW, err))
            sys.exit(3)

    # Get stats
    statsFlow = get_stats_flow()
    # retour liste de cette forme:

    """
     Reconstruction des chaines de traitement flow_source
     Création du dictionnaire de traitement
        source: 'flow_type="SFlow" flows_received_last_min="15" ip_addr="10.62.101.10" last_min="1582726323" 
                name="N/A" status="N/A" timeslice_violation="false" versions="5"'
        destination: {"IPADDR":['isExclude', 'nomCLuster', 'nbErrors', 'line']}
    
        A chaque exécution:
            - récupération du contenu du fichier pickle
            - mise à jour nomCluster et line
        
        exemple non cluster: {"10.62.101.10": ['False', 'none', '0', 'flow_type="SFlow" flows_received_last_min="15"
                ip_addr="10.62.101.10" last_min="1582726323" name="N/A" status="N/A" timeslice_violation="false"
                 versions="5"']}
        exemple est cluster: {"10.62.101.10": ['True', 'CLUSTER1', '0', 'flow_type="SFlow" flows_received_last_min="15"
                ip_addr="10.62.101.10" last_min="1582726323" name="N/A" status="N/A" timeslice_violation="false"
                 versions="5"']}
    """
    ip_addr = ""
    ipUpdate = []
    for line in statsFlow:
        # liste des valeurs de la ligne ('flow_type="SFlow"', 'flows_received_last_min="5"',
        # 'ip_addr="10.62.101.10"', ...)
        values = line.split(" ")
        for value in values:
            # updated = False
            if "ip_addr=" in value:
                ip_addr = get_ip_addr(value)
        # Liste toutes les IP actives
        ipUpdate.append(ip_addr)

        # Vérifie si l'ip fait partie d'un cluster
        isCluster, nomCluster = get_is_cluster(ip_addr)
        # print("isCluster: {} {} {}".format(ip_addr, isCluster, nomCluster))

        # Vérifie si l'ip fait partie des exclusions
        isExclude = get_is_exclude(exclude, ip_addr)
        # print("isExclude: {} {}".format(ip_addr, isExclude))

        # récupère le nombre d'erreurs du check précédent s'il existe
        nbErrors = get_existing_errors(dictListIP, ip_addr)

        # Ajoute ou mets à jour la liste
        dictListIP[ip_addr] = [isExclude, nomCluster, nbErrors, line]
        # print("ligne traitée {}: {}".format(ip_addr, dictListIP[ip_addr]))

    """
    Nettoyage du dictionnaire des ip qui n'existe plus
    """
    # récupérer la liste des ip de dictListIP
    actualList = []
    for cle in dictListIP.keys():
        actualList.append(cle)

    # Suppression des clés inexistantes dans dictListIP
    for ip in actualList:  # pour chaque ip de la liste
        if ip not in ipUpdate:  # si l'ip n'existe pas dans la nouvelle liste
            del dictListIP[ip]  # on supprime l'entrée dans le référentiel
            # print("Suppression de l'IP {} dans le dictionnaire.".format(ip))

    for ip_addr, value in dictListIP.items():
        isExclude, nomCluster, nbErrors, flow = get_values(value)
        if flow == 0 and not isExclude:  # si flow à 0 et ip non exclue on incrémente nbErrors
            nbErrors = nbErrors+1
        else:  # dans tous les autres cas on remet à 0
            nbErrors = 0

        # Mise à jour du nombre d'erreurs
        dictListIP[ip_addr][2] = nbErrors

    """
    sauvegarde du résultat dans le fichier pickle
    """
    try:
        pickle.dump(dictListIP, open(WORK_DIR+STAT_FLOW, 'wb'))
    except IOError as err:
        print("ERREUR: Impossible d'ecrire le fichier stat {} ({}).".format(WORK_DIR+STAT_FLOW, err))
        sys.exit(3)

    # analyse du résultat
    # si une ou plusieurs IP sont à trois check ou plus on remonte l'alerte
    ipErrors = {}
    # isCritical = False
    nbHosts = 0

    for ip, values in dictListIP.items():  # pour chaque entrée
        # print("ip: {}; values: {}".format(ip, values))
        isCluster, nomCluster = get_is_cluster(ip)
        if isCluster:  # si c'est un cluster
            # vérification du nombre d'erreurs sur les deux membres
            name = values[1]
            # print("name= {} {}".format(name, values))
            ip1, ip2 = get_ip_from_cluster(name)
            # print("ip1: {}={}; ip2: {}={}".format(ip1, dictListIP[ip1][2], ip2, dictListIP[ip2][2]))
            if int(dictListIP[ip1][2]) >= 3 and int(dictListIP[ip2][2]) >= 3:
                # si les deux ip du cluster sont à plus de 3 erreurs on remonte l'alerte
                ipErrors[ip1] = dictListIP[ip1][3]
                ipErrors[ip2] = dictListIP[ip2][3]
                # isCritical = True
                nbHosts = nbHosts+1
        else:  # sinon
            if values[2] >= 3:
                ipErrors[ip] = values[3]
                # isCritical = True
                nbHosts = nbHosts+1

    detailClusters = "Liste des clusters enregistrés:\n"
    for nom, ips in CLUSTERS.items():
        detailClusters += "{}: {}\n".format(nom, ips)
    if exclude != "":
        detailClusters += "Liste des ip exclues: {}\n".format(exclude)

    if nbHosts >= 1:
        status = "CRITICAL"
        message = "Le flow de {} équipement(s) est nul après trois contrôles successifs.".format(nbHosts)
        detail = "Liste des équipements concernés:\n"
        for cle, valeur in ipErrors.items():
            detail += "{}: {}\n".format(cle, valeur)
        detail += detailClusters
        perfdata = ""
    else:
        status = "OK"
        message = "Tous les équipements remontent des données."
        detail = detailClusters
        perfdata = ""
    centreon_status.exit(status, message, detail, perfdata)


def stat_licencing(warning, critical):

    capacity = ""
    flow = ""
    # Get stats
    statsResult = get_stats(URL_RIVERBED, USERNAME, PASSWORD)

    # parcourir le résultat et stocker les valeurs de chaque ligne
    for line in statsResult:
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
                    capacity = int(value.split("=")[1].replace('"', ''))
                    # print("##### mycapacity="+str(capacity))
                elif myvalue[0] == "flows_received_last_min":
                    # print(value)
                    flow = int(value.split("=")[1].replace('"', ''))
                    # print("##### myFlow="+str(flow))

    # print("Capacity:"+str(capacity)+"; Flow:"+str(flow))
    prct_flow = round(flow*100/capacity, 2)
    warn_flow = round(warning*capacity/100)
    crit_flow = round(critical*capacity/100)
    # print(str(prct_flow) +"%")
    if prct_flow >= critical:
        status = "CRITICAL"
        message = "Le flux reçu sur la dernière minute ({} soit {}%) est supérieur à {}% " \
                  "de la capacité totale de la licence ({}).".format(flow, prct_flow, critical, capacity)
        detail = ""
        perfdata = "flow={};{};{};0;{}".format(flow, warn_flow, crit_flow, capacity)
    elif prct_flow >= warning:
        status = "WARNING"
        message = "Le flux reçu sur la dernière minute ({} soit {}%) est supérieur à {}% " \
                  "de la capacité totale de la licence ({}).".format(flow, prct_flow, warning, capacity)
        detail = ""
        perfdata = "flow={};{};{};0;{}".format(flow, warn_flow, crit_flow, capacity)
    else:
        status = "OK"
        message = "Le flux reçu sur la dernière minute ({} soit {}%) est inférieur à {}%" \
                  " de la capacité totale de la licence ({}).".format(flow, prct_flow, warning, capacity)
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
        opts, args = getopt.getopt(argv, "hm:w:c:v:e", ["help", "version", "mode=", "warning=", "critical=",
                                                        "exclude="])
    except getopt.GetoptError:
        print("INCONNU: Cas non géré: {} -m <mode> -w <warning> -c <critical>".format(sys.argv[0]))
        sys.exit(3)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("{} -m <mode: licencing ou flow> -w <licencing warning capacity (%)> -c <licencing critical"
                  " capacity (%)> -e <exclusion d'adresses>".format(sys.argv[0]))
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
            print("ERREUR: les seuils warning ({}) et critical ({}) doivent être des nombres".format(warning, critical))
            sys.exit(3)

        if (warning > 100 or warning < 0) or (critical > 100 or critical < 0):
            print("ERREUR: Les seuils warning ({}) et critical ({}) doivent être compris entre"
                  " 0 et 100.".format(warning, critical))
            sys.exit(3)
        elif warning >= critical:
            print("ERREUR: le seuil warning ({}) doit être inférieur au seuil critical ({}).".format(warning, critical))
            sys.exit(3)
        stat_licencing(warning, critical)
    elif mode == "flow":
        if exclude != "":
            try:
                exclude = str(exclude).split(",")
            except Exception as e:
                print("ERREUR: la valeur {} n'est pas valide. Detail: {}".format(exclude, e))
                sys.exit(3)
        stat_flow(exclude)
    else:
        print("ERREUR: mode {} inconnu. Modes attendus: licencing ou flow uniquement.".format(mode))
        print("Script {} {}".format(sys.argv[0], VERSION))
        sys.exit(3)


if __name__ == "__main__":
    main(sys.argv[1:])
