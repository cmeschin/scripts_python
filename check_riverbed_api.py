#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" check riverbed API
    - check flow sources
    - check licencing
    2020-01-24 version 1: version initiale
    2020-02-12 version 2: Ajout mode flow
"""
#definition des constantes
VERSION = "2020-02-12 version 2"
USERNAME = "publicring"
PASSWORD = "nd7ja*!ja"

import sys
import getopt
import logging
from modules import centreon_status
from modules import tessi_common

#Modules spécifiques
import os.path
import pickle
import requests

def stat_flow(exclude):
    EXCLUDE = exclude
    nbErrors = 0
    # print("Mode non encore implémenté.")
    # sys.exit(0)

    # vérification de l'existence du fichier pickle
    dict = {}
    if os.path.exists("pickle_stat_flow"):
        dict = pickle.load(open('pickle_stat_flow', 'rb'))

    # Récupération de la page
    r = requests.get('https://riverbed-gateway.interne.tessi-techno.fr/api/gateway/1.5/stats', auth=(USERNAME, PASSWORD))

    # reformatage du résultat par ligne
    result = r.text.split( "\n")
    list_update = []
    fullline = {}
    # parcourir le résultat et stocker les valeurs de chaque ligne
    for line in result:
        flow = ""
        ipaddr = ""

        if "<flow_source flow_type" in line:
            values = line.split(" ")
            # check ipaddr
            # si ce n'est pas les clusters
            if "10.33.253.1" not in line and "10.33.253.2" not in line and "10.33.253.221" not in line and "10.33.253.222" not in line:
                for value in values:
                    updated = False
                    myvalue = value.split("=")
                    #print("myvalue:{}".format(myvalue))
                    if myvalue[0] == "flows_received_last_min":
                        flow=int(value.split("=")[1].replace('"',''))
                    elif myvalue[0] == "ipaddr":
                        ipaddr=value.split("=")[1].replace('"','')
                        list_update.append(ipaddr)
                        fullline[ipaddr] = line
                    #print("Liste update1: {}".format(list_update))
                    if flow != "" and ipaddr != "" and updated == True:
                        updated = False
                        #print("flow:{} {}".format(flow,ipaddr))
                # Ajout de l'IP dans le dictionnaire si elle n'existe pas déjà
                if ipaddr not in dict:
                    #print("Ajout de l'adresse {}.".format(ipaddr))
                    dict[ipaddr] = 0


                if flow == 0 and ipaddr not in exclude:
                    # si pas de flow, on ajoute/incrémente dans le dictionnaire
                    #print("ipaddr:{}".format(ipaddr))
                    #print("exclude: {}".format(exclude))
                    nbcheck = dict.get(ipaddr)+1
                    #print("nbcheck:{}".format(nbcheck))
                    dict[ipaddr] = nbcheck
                    #print("dict:{}".format(dict[ipaddr]))
                else:
                    nbcheck = 0
                    dict[ipaddr] = nbcheck
    # Nettoyage du dictionnaire des ip qui n'existe plus
    del_ip = []
    #print("Liste update: {}".format(list_update))
    for ip in dict.keys():
        if ip not in list_update:
            #print("IP: {}".format(ip))
            del_ip = list.append("{}".format(ip))
            #print("Suppression de l'ip {}".format(ip))

    for ip in del_ip:
        del dict[ip]
        #print("Suppression de l'IP {} dans le dictionnaire.".format(ip))

    # sauvegarde du résultat dans le fichier pickle
    pickle.dump(dict, open('pickle_stat_flow', 'wb'))

    # analyse du résultat
    # si une ou plusieurs IP sont à trois check ou plus on remonte l'alerte
    ipErrors = {}
    for cle,valeur in dict.items():
        #print("Cle: {}, Valeur: {}, ipErrors: {}".format(cle, valeur,ipErrors))
        if valeur >= 3:
            #print("Cle {}".format(cle))
            ipErrors[cle] = fullline[cle]
            nbErrors = nbErrors+1
            #print("Ajout Error: {}".format(ipErrors[cle]))

    if nbErrors >= 1:
        status = "CRITICAL"
        message = "Le flow de {} équipement(s) est nul.".format(nbErrors)
        detail = "Liste des équipements concernés:\n"
        for cle,valeur in ipErrors.items():
            detail += "{}: {}".format(cle, valeur)

        perfdata = ""
    else:
        status = "OK"
        message = "Tous les équipements remontent des données."
        detail = ""
        perfdata = ""
    centreon_status.exit(status, message, detail, perfdata)



def stat_licencing(warning,critical):

    WARN = warning
    CRIT = critical
    # Récupération de la page
    r = requests.get('https://riverbed-gateway.interne.tessi-techno.fr/api/gateway/1.5/stats', auth=(USERNAME, PASSWORD))

    # reformatage du résultat par ligne
    result = r.text.split("\n")

    # parcourir le résultat et stocker les valeurs de chaque ligne
    for line in result:
        if "<stats" in line:
            #print(line)
            #recupérer capacity et flows_received_last_min
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