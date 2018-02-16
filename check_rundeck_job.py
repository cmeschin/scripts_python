#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, getopt
import logging
import time
from urllib import request as urllib2
from xml.etree import ElementTree as ET
from modules import centreon_status
from modules import tessi_common

#CONSTANTS
RDK_ROOT_API_URL = 'http://10.33.1.53:8080/rundeck_production/api/'
RDK_EXECUTIONS_EP = '1/job/$jobId/executions'
TODAY = int(tessi_common.define_today("%w"))
NOW = int(tessi_common.define_now("%H%M"))
HOUR = int(hour.replace(":",""))

#TODO : check jour du job + check heure (arg day, hour) - pavé ci-dessous à reprendre:
#DEFINITION DE LA PERIODE D'EXECUTION DU SCRIPT
if day != TODAY or NOW < HOUR :
    status = "OK"
    message = "Heure " + hour + "d'execution non atteinte"
    centreon_status.exit(status, message)


class Execution(object):
    def __init__(self, executionId, jobName, url, status, startedAt, failedNodes=[]):
        self.executionId = executionId
        self.jobName = jobName
        self.url = url
        self.status = status
        self.startedAt = startedAt
        self.failedNodes = failedNodes

    def __str__(self):
        s = "Status: {f.status} - Trace: {f.url}\nNodes : {f.failedNodes}"
        return s.format(f=self)

def parse_nodes(element):
    return [ elementName.attrib['name'] for elementName in element.findall('node')]

def parse_exec(node):
    failedNodes = [parse_nodes(elt) for elt in node.iter('failedNodes')]
    return Execution(node.attrib['id'], node.find('job/name').text, node.attrib['href'], node.attrib['status'],  node.find('date-started').attrib['unixtime'], failedNodes)

def parse_execution(authToken, jobId, limit):

    apiUrl = RDK_ROOT_API_URL \
             + RDK_EXECUTIONS_EP.replace('$jobId', jobId) \
             + '?authtoken=' + authToken \
             + '&max=' + limit
    logging.debug('Calling ' + apiUrl)
    root = query_api(apiUrl)
    return [parse_exec(node) for node in root.iter('execution')]

def query_api(apiUrl):
    xmlDocument = ET.parse(urllib2.urlopen(apiUrl)).getroot()
    return xmlDocument

def main(argv):
    action = ''
    authToken = ''
    jobId = ''
    try:
        opts, args = getopt.getopt(argv, "ha:c:j:i:ll:t:w:d:H:",["action=", "critical=", "job=", "limit=", "log-level=", "token=", "warning=","day=", "hour="])
    except getopt.GetoptError:
        print('INCONNU: Cas non géré: executions.py -a <action> -j <jobId> -l <limit> -t <token> -d <day> -H <hour>')
        sys.exit(3)
    for opt, arg in opts:
        if opt == '-h':
            print('executions.py -a <action> -j <jobId> -l <limit> -t <token>')
            sys.exit(0)
        elif opt in ("-a", "--action"):
            action = arg
        elif opt in ("-c", "--critical"):
            criticalThreshold = arg
        elif opt in ("-j", "--job"):
            jobId = arg
        elif opt in ("-l", "--limit"):
            limit = arg
        elif opt in ("-t", "--token"):
            authToken = arg
        elif opt in ("-ll", "--log-level"):
            logLevel = arg
            numeric_level = getattr(logging, logLevel.upper(), None)
        elif opt in ("-w", "--warning"):
            warningThreshold = arg
        elif opt in ("-d", "--day"):
            day = int(arg)
        elif opt in ("-H", "--hour"):
            hour = arg

    if not 'logLevel' in locals():
        logLevel = 'DEBUG'
        numeric_level = getattr(logging, logLevel.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % logLevel)

    logging.basicConfig(format='[%(asctime)s] - [%(levelname)s] : %(message)s', level=numeric_level)

    logging.debug('Action set to ' + action)
    logging.debug('JobId set to ' + jobId)
    logging.debug('Limit set to ' + limit)
    logging.debug('Token set to ' + authToken)

    errorsFound = 0
    warningsFound = 0
    runningTooLong = 0
    runningsFound = 0
    if action == 'executions':
        executions = parse_execution(authToken, jobId, limit)
        for execution in executions:
            currentJobName = execution.jobName
            if execution.status == 'failed':
                errorsFound += 1
            elif execution.status == 'aborted':
                warningsFound += 1
            elif execution.status == 'killed':
                warningsFound += 1
            elif execution.status == 'running':
                currentTime = int(time.time())
                runningsFound +=1
        if errorsFound > 0:
            print('CRITIQUE - ' + currentJobName + ' failed')
            print( str(errorsFound) + ' execution(s) error')
            print (str(warningsFound) + ' execution(s) killed/aborted')
            print (str(runningsFound) + ' execution(s) running')
            for execution in executions:
                if execution.status == 'failed':
                    print (execution)
                if execution.status == 'killed':
                    print (execution)
            sys.exit(2)
        elif warningsFound > 0:
            #TODO: implémenter le code de sortie
            print ('WARNING - Job ' + currentJobName + ' - ' + str(errorsFound) + ' execution(s) killed/aborted')
        elif runningsFound > 0:
            # TODO: calculer le temps d'exécution en fonction des seuils de temps
            # TODO:	Implémenter la notion de job Running avec seuil warning / critique. (ie warning si > 5 heures, critique si > à 8 heures)

            print ('WARNING - Job ' + currentJobName + ' - ' + str(errorsFound) + ' execution(s) running')
            sys.exit(0)
        else:
            print ('OK - Aucune erreur pour le job ' + currentJobName)
            sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])